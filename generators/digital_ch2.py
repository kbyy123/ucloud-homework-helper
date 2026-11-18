"""Verified, source-bound solutions for digital logic chapter 2 homework.

This generator never logs into Ucloud or submits work. Diagram anomalies are
kept as drawn, following the user's explicit choice on 2026-10-19.
"""
import argparse
import hashlib
import itertools
import json
import re
import shutil
from pathlib import Path
from PIL import Image
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parent.parent
BANK=ROOT/'题库'/'digital-logic-7'
CATALOGUE=ROOT/'题库'/'页面索引'/'digital-logic-7'
BOOK=ROOT.parent/'26fa-数字逻辑与数字系统'/'数字逻辑.pdf'
REFS=['2/2','2/3','2/5','2/6','2/7','2/9','2/10']
QUESTIONS={
 '2/2':'分析图 P2.2 所示逻辑电路，其中 $S_3$、$S_2$、$S_1$、$S_0$ 为控制输入端，列出真值表，说明 $F$ 与 $A$、$B$ 的关系。',
 '2/3':'分析图 P2.3 所示逻辑电路，列出真值表，说明其逻辑功能。',
 '2/5':'分析图 P2.5 所示逻辑电路，列出真值表，说明其逻辑功能。',
 '2/6':'图 P2.6 所示为两种十进制数代码转换器，输入为余3码，分析输出是什么代码。',
 '2/7':'图 P2.7 所示是一个受 $M$ 控制的4位二进制码和循环码的相互转换电路。$M=1$ 时，完成何种转换？$M=0$ 时，完成何种转换？请分析之。',
 '2/9':'用红、黄、绿三个指示灯表示三台设备的工作情况：绿灯亮表示全部正常；红灯亮表示有一台不正常，黄灯亮表示两台不正常；红、黄灯全亮表示三台都不正常。列出控制电路真值表，并选用合适的逻辑门电路来实现。',
 '2/10':'用两片双四选一数据选择器和与非门实现循环码至8421BCD码转换。',
}
FIGURES={f'2/{n}':f'P2.{n}' for n in [2,3,5,6,7]}
BOXES={'P2.2':(180,390,990,1010),'P2.3':(970,390,1740,1010),
       'P2.5':(930,1160,1730,1720),'P2.6':(200,1830,1000,2440),'P2.7':(950,1830,1760,2440)}
GRAY16=[0,1,3,2,6,7,5,4,12,13,15,14,10,11,9,8]  # textbook Table 1.1
GRAY_DECIMAL=[0,1,3,2,6,14,10,8,12,13]  # different code: textbook Table 1.2

def digest(data):return hashlib.sha256(data).hexdigest()
def fresh(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=text.encode('utf-8')
    if path.exists():
        if path.read_bytes()!=data:raise FileExistsError(f'Preserving existing file: {path}')
    else:path.write_bytes(data)
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+
                    ['| '+' | '.join(str(x) for x in row)+' |' for row in rows])+'\n'
def bits(n,width):return tuple(map(int,format(n,f'0{width}b')))
def word(seq):return ''.join(map(str,seq))
def inv(x):return 1-int(bool(x))
def nand(*xs):return inv(all(xs))
def nor(*xs):return inv(any(xs))
def mux4(s1,s0,ds):return ds[2*s1+s0]
def nand_xor(a,b):
    t=nand(a,b);return nand(nand(a,t),nand(b,t))

def gate2(a,b,s3,s2,s1,s0):
    # Five AND gates, two NORs and a final AND. The last AND is unary.
    upper=nor(a*b*s2,a*inv(b)*s3)
    lower=nor(inv(b)*s1,b*s0,a)
    return upper*lower
def gate3(a,b,c):
    f1=nor(a*inv(b)*c,a*b*inv(c),inv(a)*b*c,inv(b)*inv(c))
    f2=nor(inv(a)*inv(b),inv(a)*inv(c),inv(b)*inv(c))
    return f1,f2
def gate5(a1,a0,xs):
    x0,x1,x2,x3=xs
    return nand(nand(x0,inv(a1),inv(a0)),nand(x1,inv(a1),a0),nand(x2,a1,inv(a0)),nand(x3,a1,a0))
def gate6(a,b,c,d):
    w=nand(nand(a,c,d),nand(a,b))
    x=nand(nand(b,c,d),nand(inv(b),inv(d)),nand(inv(b),inv(c)))
    y=nand(nand(c,inv(d)),nand(inv(c),d))
    return w,x,y,inv(d)
def gate7(m,x):
    x3,x2,x1,x0=x;y3=x3;y2=x2^x3
    t1=nand(nand(m,x2),nand(inv(m),y2));y1=x1^t1
    t0=nand(nand(m,x1),nand(inv(m),y1));y0=x0^t0
    return y3,y2,y1,y0
def mux10(g,decimal=False):
    g3,g2,g1,g0=g
    ng1=nand(g1,g1);h=nand_xor(g1,g0)
    if decimal:
        g1_or_g0=nand(ng1,nand(g0,g0))
        data=[[0,0,0,ng1],[0,1,1,g1],[g1,0,1,0],[h,0,ng1,g1_or_g0]]
    else:data=[[0,0,1,1],[0,1,1,0],[g1,ng1,ng1,g1],[h,nand(h,h),nand(h,h),h]]
    return tuple(mux4(g3,g2,d) for d in data)

def verify():
    counts={};computed={}
    count=0
    for a,b,s3,s2,s1,s0 in itertools.product([0,1],repeat=6):
        # Independent behavioral model: A forces off; B selects S1 or S0.
        expected=0 if a else inv(s0 if b else s1)
        assert gate2(a,b,s3,s2,s1,s0)==expected
        count+=1
    counts['2/2']=count
    computed['2/2']=[[word(s),*[gate2(a,b,*s) for a,b in itertools.product([0,1],repeat=2)]] for s in itertools.product([0,1],repeat=4)]
    computed['2/3']=[]
    for a,b,c in itertools.product([0,1],repeat=3):
        f1,f2=gate3(a,b,c);n=4*a+2*b+c
        assert f1==int(n in {1,2,7}) and f2==int(a+b+c>=2)
        assert f1==((inv(a)*inv(b)*c)|(inv(a)*b*inv(c))|(a*b*c))
        computed['2/3'].append([a,b,c,f1,f2])
    counts['2/3']=8
    for a1,a0,*xs in itertools.product([0,1],repeat=6):assert gate5(a1,a0,xs)==xs[2*a1+a0]
    counts['2/5']=64
    computed['2/6']=[]
    for n in range(16):
        a,b,c,d=bits(n,4);actual=gate6(a,b,c,d)
        assert actual==((a*b)|(a*c*d),(b*c*d)|(inv(b)*inv(c))|(inv(b)*inv(d)),c^d,inv(d))
        if 3<=n<=12:
            assert word(actual)==format(n-3,'04b')
            computed['2/6'].append([n-3,format(n,'04b'),word(actual)])
    counts['2/6']=16
    computed['2/7']=[]
    for n in range(16):
        x=bits(n,4)
        assert word(gate7(1,x))==format(GRAY16[n],'04b')
        assert word(gate7(0,x))==format(GRAY16.index(n),'04b')
        computed['2/7'].append([format(n,'04b'),word(gate7(1,x)),word(gate7(0,x))])
    counts['2/7']=32
    red=[1,0,0,1,0,1,1,0];yellow=[1,1,1,0,1,0,0,0];green=[0,0,0,0,0,0,0,1]
    computed['2/9']=[]
    for n in range(8):
        a,b,c=bits(n,3);failed=3-(a+b+c);expect=(int(failed in [1,3]),int(failed in [2,3]),int(failed==0))
        actual=(red[n],yellow[n],green[n])
        assert actual==expect
        assert actual==(inv(a^b^c),int(a+b+c<=1),a*b*c)
        computed['2/9'].append([a,b,c,failed,*actual])
    counts['2/9']=8
    computed['2/10']=[]
    for n,g in enumerate(GRAY16):
        assert word(mux10(bits(g,4)))==format(n,'04b')
        if n<10:computed['2/10'].append([n,format(g,'04b'),word(mux10(bits(g,4)))])
    counts['2/10_table_1_1']=16
    computed['2/10_alternative']=[]
    for n,g in enumerate(GRAY_DECIMAL):
        assert word(mux10(bits(g,4),True))==format(n,'04b')
        computed['2/10_alternative'].append([n,format(g,'04b'),word(mux10(bits(g,4),True))])
    counts['2/10_table_1_2']=10
    return {'ok':True,'caseCounts':counts,'inputCases':sum(counts.values()),'computed':computed,
            'checks':['按原图逐门求值与化简表达式比对','全部选择器地址及数据输入穷举','余3码十个合法码字逐一验证',
                      '循环码按原书表1.1独立码表验证，不用生成公式充当唯一对照',
                      '按设备故障数核对三色指示灯，包含三台故障红黄同时亮',
                      '第10题分别核验表1.1循环二进制码和表1.2十进制格雷码，编码不混用'],
            'sourceNotes':['用户确认没有勘误，按原图分析并注明疑点；未补接假设的连线。',
                           '第2题最下方与门按图中的单输入同相缓冲处理；S3和S2被吸收。',
                           '第3题F1所接第四个与门为B反和C反两输入，故原图不是标准全加器。']}

def solutions(checks):
    c=checks['computed'];s={}
    s['2/2']=r'''按你确认的方式，严格保留图 P2.2 的连线。最下方与门只画出 $A$ 一路输入，按单输入与门（同相缓冲）处理；不补接任何未画出的控制线。

从上到下五个与门的输出依次为

$$T_1=ABS_2,\quad T_2=A\overline B S_3,\quad T_3=\overline B S_1,\quad T_4=BS_0,\quad T_5=A.$$

两个或非门后接与门，因此

$$F=\overline{ABS_2+A\overline B S_3}\;\overline{\overline B S_1+BS_0+A}.$$

第二因子在 $A=1$ 时为0；在 $A=0$ 时第一因子恒为1，故吸收化简得

$$\boxed{F=\overline A\,\overline{\overline B S_1+BS_0}
=\overline A(\overline B\,\overline{S_1}+B\overline{S_0}).}$$

下面以每行四个输出覆盖 $AB=00,01,10,11$，共列全64种输入组合：

'''+table(['$S_3S_2S_1S_0$','$F(00)$','$F(01)$','$F(10)$','$F(11)$'],c['2/2'])+r'''
控制关系可压缩为：

'''+table(['$S_1S_0$','$F$'],[['00',r'$\overline A$'],['01',r'$\overline A\,\overline B$'],['10',r'$\overline A B$'],['11','0']])+r'''
**原图疑点：** 按现有连线，$S_3,S_2$ 对最终输出无影响；这与“四个控制端均可选功能”的常见设计不同。此结论是原图的吸收结果，不能为了得到常见电路而擅自补线。若教师后续给出更正图，应重做本题。
'''
    s['2/3']=r'''由三个反相器先得到 $\overline A,\overline B,\overline C$。接到上方或非门的四个乘积项按原图分别为

$$A\overline B C,\quad AB\overline C,\quad \overline A BC,\quad \overline B\,\overline C.$$

注意第四项只有两个输入，没有补接 $\overline A$。于是

$$F_1=\overline{A\overline B C+AB\overline C+\overline A BC+\overline B\,\overline C}
=\overline A\,\overline B C+\overline A B\overline C+ABC
=\sum m(1,2,7).$$

下方三个与门为 $\overline A\overline B,\overline A\overline C,\overline B\overline C$，故

$$\boxed{F_2=\overline{\overline A\overline B+\overline A\overline C+\overline B\overline C}=AB+AC+BC.}$$

'''+table(['$A$','$B$','$C$','$F_1$','$F_2$'],c['2/3'])+r'''
逻辑功能：$F_2$ 是三输入多数表决函数（至少两个输入为1时输出1）。$A=0$ 时 $F_1=B\oplus C$；$A=1$ 时 $F_1=BC$。

**原图疑点：** 它按现有连线不是标准全加器：输入 $ABC=100$ 时原图 $F_1=0$，而全加器和位应为1。若第四个与门原本应为 $\overline A\overline B\overline C$，才会得到标准和位 $A\oplus B\oplus C$；本解答没有采用这个未经教师确认的改图。
'''
    rows=[]
    for sel in range(4):
        for selected in [0,1]:
            xs=['—']*4;xs[sel]=selected;rows.append([*bits(sel,2),*reversed(xs),selected])
    s['2/5']=r'''先对四个与非门以及末级与非门使用德摩根律：

$$\boxed{F=X_0\overline{A_1}\overline{A_0}+X_1\overline{A_1}A_0+X_2A_1\overline{A_0}+X_3A_1A_0.}$$

其真值表可按无关输入压缩如下。“—”表示该未选中数据位取0或1均不影响结果；表中8行覆盖全部64种输入组合。

'''+table(['$A_1$','$A_0$','$X_3$','$X_2$','$X_1$','$X_0$','$F$'],rows)+r'''
**结论：这是四选一数据选择器。** 地址 $A_1A_0=00,01,10,11$ 时，分别有 $F=X_0,X_1,X_2,X_3$，可写为 $F=X_{2A_1+A_0}$。
'''
    s['2/6']=r'''把每组与非—与非结构改写成“与—或”式，按原图连线可得

$$\boxed{\begin{aligned}
W&=AB+ACD,\\
X&=BCD+\overline B\overline D+\overline B\overline C,\\
Y&=C\overline D+\overline C D=C\oplus D,\\
Z&=\overline D.
\end{aligned}}$$

输入 $ABCD$ 为十进制数字的余3码，即数字 $n$ 对应二进制 $n+3$。逐个代入十个合法输入：

'''+table(['十进制数字','$ABCD$（余3码）','$WXYZ$'],c['2/6'])+r'''
输出依次为0000至1001，其位权依次为8、4、2、1。因此 **本电路实现余3码→8421BCD码转换**。

输入0000、0001、0010、1101、1110、1111不是本题余3码的合法数字码字，不把它们当作十进制数字参与转换结论。
'''
    s['2/7']=r'''图中三只异或门及两组“与非—与非”选择网络给出

$$\begin{aligned}
Y_3&=X_3,\\
Y_2&=X_2\oplus X_3,\\
Y_1&=X_1\oplus(MX_2+\overline M Y_2),\\
Y_0&=X_0\oplus(MX_1+\overline M Y_1).
\end{aligned}$$

当 $M=1$ 时，选择网络取 $X_2,X_1$：

$$Y_3=X_3,\quad Y_2=X_3\oplus X_2,\quad Y_1=X_2\oplus X_1,\quad Y_0=X_1\oplus X_0.$$

所以 **$M=1$ 实现自然二进制码→表1.1循环二进制码（反射格雷码）**。

当 $M=0$ 时，选择网络取 $Y_2,Y_1$：

$$Y_3=X_3,\quad Y_2=X_3\oplus X_2,\quad Y_1=X_3\oplus X_2\oplus X_1,\quad Y_0=X_3\oplus X_2\oplus X_1\oplus X_0.$$

所以 **$M=0$ 实现表1.1循环二进制码→自然二进制码**。两组选择器反馈只从高位结果向低位传播，是组合逻辑级联，没有时序存储。

'''+table(['输入 $X_3X_2X_1X_0$','$M=1$ 输出','$M=0$ 输出'],c['2/7'])
    s['2/9']=r'''按老师补充要求，用八选一数据选择器实现。约定 $A,B,C=1$ 表示相应设备正常；$R,Y,G=1$ 表示红、黄、绿灯点亮。

'''+table(['$A$','$B$','$C$','故障台数','$R$','$Y$','$G$'],c['2/9'])+r'''
从表中得到（最小项编号按 $ABC$ 从高到低排列）：

$$\begin{aligned}
R&=\sum m(0,3,5,6)=\overline{A\oplus B\oplus C},\\
Y&=\sum m(0,1,2,4)=\overline A\overline B+\overline A\overline C+\overline B\overline C,\\
G&=\sum m(7)=ABC.
\end{aligned}$$

选择 **三路八选一选择器**（每个输出占一路），三路共用地址 $S_2=A,S_1=B,S_0=C$，使能端置为有效状态。取正逻辑输出 $Q=D_{4A+2B+C}$，数据端固定接0或1：

'''+table(['输出路','$D_0$','$D_1$','$D_2$','$D_3$','$D_4$','$D_5$','$D_6$','$D_7$'],[['红灯R',1,0,0,1,0,1,1,0],['黄灯Y',1,1,1,0,1,0,0,0],['绿灯G',0,0,0,0,0,0,0,1]])+r'''
![第9题八选一实现](images/q9-mux.svg)

如实际器件另有反相输出，必须选与上表一致的正相输出，或在输出端补反相。灯的限流和驱动按实验器材配置；上图表示逻辑连接。

题干原有“逻辑门实现”的等价式也已列出，但本题最终方案使用老师指定的八选一结构。特别注意 $ABC=000$ 时红、黄灯同时亮，不能设计成三个输出始终互斥的指示器。
'''
    s['2/10']=r'''先明确编码：本题主方案采用原书书页8、PDF第16页 **表1.1的循环二进制码**，与第7题的互换电路一致。它的数字5、6、7分别为0111、0101、0100。该页表1.2另列一套十进制格雷码，5、6、7分别为1110、1010、1000，不能混用；文末另给这套编码的接线备选。

设输入循环码为 $G_3G_2G_1G_0$，输出8421BCD为 $B_3B_2B_1B_0$。对合法数字0–9，真值对应为：

'''+table(['数字','表1.1循环码','8421BCD'],c['2/10'])+r'''
按循环码逆变换：

$$B_3=G_3,\quad B_2=G_3\oplus G_2,\quad B_1=G_3\oplus G_2\oplus G_1,\quad B_0=G_3\oplus G_2\oplus G_1\oplus G_0.$$

两片“双四选一”共有四路四选一，分别负责四个输出。两片共用选择端 $S_1=G_3,S_0=G_2$，各路使能有效。定义 $H=G_1\oplus G_0$，按选择地址00、01、10、11展开得到接线表：

'''+table(['芯片/通道','输出','$D_0$','$D_1$','$D_2$','$D_3$'],[['U1-A',r'$B_3$','0','0','1','1'],['U1-B',r'$B_2$','0','1','1','0'],['U2-A',r'$B_1$',r'$G_1$',r'$\overline{G_1}$',r'$\overline{G_1}$',r'$G_1$'],['U2-B',r'$B_0$','$H$',r'$\overline H$',r'$\overline H$','$H$']])+r'''
所有辅助反相及异或均用与非门搭建，不另用异或芯片：令 $N(x,y)=\overline{xy}$，连接

$$\begin{aligned}
L&=N(G_1,G_0),&P&=N(G_1,L),&Q&=N(G_0,L),\\
H&=N(P,Q),&\overline H&=N(H,H),&\overline{G_1}&=N(G_1,G_1).
\end{aligned}$$

因此主方案共使用 **两片双四选一＋六个二输入与非门**。反相使用与非门的两个输入并接；图中 $B_3$ 也通过U1-A输出，以完整给出四路连接。选择器输出采用同相型，地址定义必须与接线表一致。

![第10题两片双四选一实现](images/q10-mux.svg)

输入不是合法数字0–9的码字时，本题不要求输出有效BCD。这里保留普通4位循环码逆变换，对相应10–15会输出1010–1111，不能将其解释为一位合法BCD。

### 若课程采用表1.2的十进制格雷码

为避免两套教材编码混淆，下面给出完整备选；这是另一编码表的独立方案，不能只替换主方案真值表而沿用主方案接线。

'''+table(['数字','表1.2格雷码','8421BCD'],c['2/10_alternative'])+r'''
仍令两片选择端 $S_1=G_3,S_0=G_2$、各路使能有效，使用下表替换四路数据端：

'''+table(['输出','$D_0$','$D_1$','$D_2$','$D_3$'],[[r'$B_3$','0','0','0',r'$\overline{G_1}$'],[r'$B_2$','0','1','1',r'$G_1$'],[r'$B_1$',r'$G_1$','0','1','0'],[r'$B_0$','$H$','0',r'$\overline{G_1}$',r'$G_1+G_0$']])+r'''
其中 $H$ 仍用四个与非门产生，另用 $N(G_1,G_1)$、$N(G_0,G_0)$ 和 $N(\overline{G_1},\overline{G_0})$ 产生所需的反相信号及 $G_1+G_0$。总计两片双四选一＋七个二输入与非门。该备选已逐一核验表1.2的十个合法码字，其余六码字视为无关输入。
'''
    return s

def diagram9():
    blocks=[]
    for i,(name,values) in enumerate([('R',[1,0,0,1,0,1,1,0]),('Y',[1,1,1,0,1,0,0,0]),('G',[0,0,0,0,0,0,0,1])]):
        x=40+i*360
        blocks.append(f'<rect x="{x}" y="55" width="290" height="355" rx="12" fill="#edf4ff" stroke="#225995" stroke-width="2"/><text x="{x+145}" y="89" text-anchor="middle">8:1 MUX ({name})</text>')
        for n,v in enumerate(values):blocks.append(f'<text x="{x+22}" y="{124+n*29}">D{n} = {v}</text>')
        blocks.append(f'<path d="M {x+290} 220 h 33" stroke="#222" stroke-width="2"/><text x="{x+310}" y="211">{name}</text><text x="{x+22}" y="388">S2=A, S1=B, S0=C</text>')
    return svg(1110,475,'Three status outputs; use positive outputs; enable all channels',blocks)
def diagram10():
    blocks=[]
    data=[('U1',[('B3',['0','0','1','1']),('B2',['0','1','1','0'])]),('U2',[('B1',['G1','~G1','~G1','G1']),('B0',['H','~H','~H','H'])])]
    for chip,(name,channels) in enumerate(data):
        x=35+chip*555
        blocks.append(f'<rect x="{x}" y="52" width="500" height="440" rx="10" fill="#f6f9fc" stroke="#225995" stroke-width="2"/><text x="{x+250}" y="85" text-anchor="middle">{name}: dual 4:1 MUX</text>')
        for j,(output,ds) in enumerate(channels):
            y=110+j*167
            blocks.append(f'<rect x="{x+40}" y="{y}" width="320" height="145" fill="#e9f2ff" stroke="#225995"/><text x="{x+205}" y="{y+25}" text-anchor="middle">channel {chr(65+j)}</text>')
            for k,value in enumerate(ds):blocks.append(f'<text x="{x+60}" y="{y+50+k*26}">D{k} = {value}</text>')
            blocks.append(f'<path d="M {x+360} {y+74} h 65" stroke="#222" stroke-width="2"/><text x="{x+432}" y="{y+82}">{output}</text>')
        blocks.append(f'<text x="{x+35}" y="470">S1=G3, S0=G2; enable both channels</text>')
    blocks.append('<text x="45" y="535">N(x,y)=~(xy). L=N(G1,G0); P=N(G1,L); Q=N(G0,L); H=N(P,Q).</text><text x="45" y="570">~H=N(H,H); ~G1=N(G1,G1). Six 2-input NAND gates in total.</text>')
    return svg(1120,630,'Table 1.1 code: two dual MUX chips + NAND-only auxiliary logic',blocks)
def svg(width,height,title,blocks):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><g font-family="Segoe UI,Arial,sans-serif" font-size="19" fill="#162536"><text x="30" y="30">{title}</text>'+''.join(blocks)+'</g></svg>\n'

def prepare():
    source_index=json.loads((CATALOGUE/'index.json').read_text(encoding='utf-8'))
    assert digest(BOOK.read_bytes())==source_index['sourceSha256'],'Textbook changed'
    images=BANK/'images';images.mkdir(parents=True,exist_ok=True)
    for page in [66,67]:
        dest=images/f'pdf-{page:04}.png'
        if not dest.exists():shutil.copyfile(CATALOGUE/'images'/dest.name,dest)
    if not (images/'pdf-0016.png').exists():
        pdf=pdfium.PdfDocument(str(BOOK));page=pdf[15];bitmap=page.render(scale=2600/max(page.get_size()))
        bitmap.to_pil().save(images/'pdf-0016.png',optimize=True);bitmap.close();page.close();pdf.close()
    with Image.open(images/'pdf-0066.png') as page:
        for name,box in BOXES.items():
            path=images/(name+'.png')
            if not path.exists():page.crop(box).save(path,optimize=True)
    fresh(images/'q9-mux.svg',diagram9());fresh(images/'q10-mux.svg',diagram10())
    exercises=[]
    for ref,text in QUESTIONS.items():
        number=int(ref.split('/')[1]);pdfpage=66 if number in [2,3,5,6] else 67
        statement=f'## 第2章第{number}题\n\n来源：《数字逻辑》第七版，书页{pdfpage-8} / PDF第{pdfpage}页。\n\n{text}\n'
        if ref in FIGURES:statement+=f'\n![原书图{FIGURES[ref]}](../images/{FIGURES[ref]}.png)\n'
        if number==7:statement+='\n图P2.7位于前一页：书页58 / PDF第66页。\n'
        fresh(BANK/'2'/f'{number}.md',statement)
        exercises.append({'key':ref,'file':f'2/{number}.md','sha256':digest(statement.encode('utf-8')),'reviewed':True,
                          'printedPage':pdfpage-8,'pdfPage':pdfpage,'dependencies':[16] if number in [6,7,10] else [],
                          'sourceNote':'用户确认按原图分析，连线疑点保留' if number in [2,3] else ''})
    index={'schema':1,'bookId':'digital-logic-7','courseBookId':'digital-logic-pending','title':'数字逻辑','edition':'第七版·立体化教材',
           'textbook':str(BOOK),'sha256':source_index['sourceSha256'],'scope':'仅第二章本次7题已转录、作答和程序核验；不是全书已解答',
           'generator':'digital_ch2.py','exercises':exercises,
           'images':[{'file':'images/'+p.name,'sha256':digest(p.read_bytes())} for p in sorted(images.iterdir()) if p.is_file()]}
    fresh(BANK/'index.json',json.dumps(index,ensure_ascii=False,indent=2)+'\n')

def references(source):
    if source['course']['key']!='数字逻辑' or source['course']['bookId'] not in ['digital-logic-pending','digital-logic-7']:
        raise ValueError('Wrong course/book binding')
    if source.get('chapter')!='第二章 组合逻辑':raise ValueError('Chapter is not verified')
    text=re.sub(r'[（(][^）)]*[）)]','',source['requirements']).replace('\n','').strip()
    if not re.fullmatch(r'课后题\s*\d+(?:\s*[、，,]\s*\d+)*[。.]?\s*',text):raise ValueError('Unrecognized requirements')
    refs=[f'2/{n}' for n in re.findall(r'\d+',text)]
    if refs!=REFS:raise ValueError('This generator is verified only for the seven specified exercises')
    if source.get('attachments') or source.get('resources'):raise ValueError('Additional source attachments require review')
    if '八选一数据选择器' not in source['requirements']:raise ValueError('Teacher-specific implementation requirement changed')
    return refs

def build(source_path,out):
    source=json.loads(Path(source_path).read_text(encoding='utf-8'));refs=references(source);out=Path(out)
    index=json.loads((BANK/'index.json').read_text(encoding='utf-8'))
    if digest(BOOK.read_bytes())!=index['sha256']:raise ValueError('Textbook hash changed')
    for item in index['exercises']:
        if digest((BANK/item['file']).read_bytes())!=item['sha256']:raise ValueError('Transcription changed')
    for item in index['images']:
        if digest((BANK/item['file']).read_bytes())!=item['sha256']:raise ValueError('Source figure changed')
    checks=verify();answers=solutions(checks)
    shutil.copytree(BANK/'images',out/'images')
    questions=[f"# 题目：{source['title']}\n",f"课程：{source['course']['name']}\n\n待办ID：{source['id']}\n\n截止：{source['due']}（北京时间）\n",
               '## 云邮原始要求\n\n'+source['requirements']+'\n','附件列表为空。老师对第9题的八选一要求和第9、10题的“本周五课后再做”说明均保留；按你本次要求现在生成学习材料。\n',
               '教材：《数字逻辑》第七版·立体化教材（白中英、朱立东主编）。以下题干依原书转录，图形保留原图。\n']
    for item in index['exercises']:
        if item['key'] in refs:questions.append((BANK/item['file']).read_text(encoding='utf-8').replace('../images/','images/'))
    questions+=['## 原书整页核对\n','![书页58，PDF66](images/pdf-0066.png)\n','![书页59，PDF67](images/pdf-0067.png)\n',
                '编码依据：书页8 / PDF第16页。上表1.1和下表1.2采用不同的循环/格雷编码，解答明确区分。\n\n![原书编码表](images/pdf-0016.png)\n']
    fresh(out/'题目.md','\n'.join(questions))
    answer=[f"# 解答：{source['title']}\n",'约定：逻辑加号表示或，相乘表示与，上划线表示非，$\\oplus$ 表示异或。输入码字均按下标从高到低书写。\n',
            '**原图处理已获你确认：第2、3题严格按原图分析并注明疑点，不擅自补接连线。** 第10题主方案按表1.1，另附表1.2不同码制的备选接线。\n']
    for ref in refs:answer.append(f'## 第2章第{ref.split("/")[1]}题\n\n'+answers[ref])
    fresh(out/'解答.md','\n'.join(answer))
    record=[f"# 核对记录：{source['title']}\n",'状态：7题原题、原图和中文解答已整理；程序验证通过。用户明确选择按原图分析并注明疑点。没有向云邮保存或提交。\n',
            '## 作业来源\n',f"课程ID：`{source['course']['id']}`；待办ID：`{source['id']}`。课程归属来自课程活动ID关联，题号来自作业详情正文；不是从标题猜题。\n",
            f"教材SHA-256：`{index['sha256']}`。\n",
            table(['题号','书页/PDF页','原图或依赖'],[[r,'58 / 66' if r in ['2/2','2/3','2/5','2/6'] else '59 / 67',FIGURES.get(r,'无题图')+('；图在书页58/PDF66' if r=='2/7' else '')] for r in refs]),
            '第6、7、10题同时核对书页8/PDF16的编码表。原图按整页与局部图双份保存。\n',
            '## 逐门核对\n',
            '- 图P2.2上两与门为ABS₂、AB̄S₃，下三与门为B̄S₁、BS₀、A。最下门没有补接未画出的输入。\n',
            '- 图P2.3的上方第四与门只有B̄、C̄；不擅自改成ĀB̄C̄。原图F₁与全加器和位在ABC=100处不同。\n',
            '- 图P2.5核对两个选择信号反相器、四个三输入与非门与末级与非门。\n',
            '- 图P2.6核对W的ACD和AB、X的BCD/B̄D̄/B̄C̄、Y的两异或乘积、Z的D反。\n',
            '- 图P2.7的M=1选择X₂/X₁，M=0选择Y₂/Y₁；没有把转换方向弄反。\n',
            '## 原书差异与边界\n',
            '- 第2、3题的连线疑点已向你说明，你回复“没有勘误，按原图分析并注明疑点”。解答使用原图，不把可能的更正当成事实。\n',
            '- 表1.1的循环二进制码与表1.2十进制格雷码在5、6、7处不同，第10题分别提供并验证两套方案，主方案采用与第7题一致的表1.1。\n',
            '- 第9题按三个设备故障数定义所有8种状态；三故障时红黄同时亮。最终使用八选一选择器，未以纯门电路替代教师指定实现。\n',
            '- 第10题采用功能级双四选一通道连接和NAND网表，未虚构特定芯片管脚号。实际芯片的地址位次、有效使能和正相输出须与接线表一致。\n',
            '## 独立计算验证\n',table(['检查','穷举输入数'],list(checks['caseCounts'].items())),
            f"合计{checks['inputCases']}个输入用例，包含全部门电路组合、全部选择地址、余3合法码字、两套编码表及三设备状态。复核脚本为项目digital_ch2.py --verify。\n",
            '程序验证检验的是已转录门级网表与独立功能模型的一致性，不替代对原图连线的视觉核对。\n',
            '## 重跑\n','通过archive()原子归档；相同来源与材料跳过，人工修改保留，来源或材料更新进入revisions。只有verification.json通过后才记处理成功。\n']
    fresh(out/'核对记录.md','\n'.join(record))
    fresh(out/'verification.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--verify',action='store_true');parser.add_argument('--source');parser.add_argument('--out')
    args=parser.parse_args()
    if args.prepare:prepare();print(json.dumps({'ok':True,'prepared':REFS}))
    elif args.verify:
        checks=verify();print(json.dumps({k:v for k,v in checks.items() if k!='computed'},ensure_ascii=True,indent=2))
    elif args.source and args.out:build(args.source,args.out);print(json.dumps({'ok':True}))
    else:parser.error('choose --prepare, --verify, or --source FILE --out DIR')
