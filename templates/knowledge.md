这次作业实际上覆盖了概率论中一个非常重要的知识模块：**数学期望 → 方差 → 协方差 → 相关系数 → 随机变量函数的分布与期望**。

我看完了整份作业。建议不要直接开始刷题，而是先把下面这些知识点补齐。尤其是期望、方差、协方差这三个概念，它们是后面所有题目的基础。

我按照作业的知识结构讲解，并且假设你已经掌握随机变量、概率分布、边缘分布、联合分布和独立性的基本概念。

# **一、数学期望（最重要的基础）**

## **1. 什么是数学期望？**

数学期望（Mathematical Expectation），也叫均值（Mean）。

直观理解：**随机变量所有可能取值的加权平均值，权重就是对应的概率。**

例如，随机变量 $X$ 的分布为：

| $X$ 的取值 | 1   | 2   | 3   |
| ----------- | --- | --- | --- |
| 概率          | 0.2 | 0.5 | 0.3 |

那么：

$$
E(X)=1\times0.2+2\times0.5+3\times0.3
$$

$$
=2.1
$$

注意，期望不一定是随机变量实际可能取到的值。这里 $X$ 只能取 1、2、3，但是期望是 2.1。

## **2. 离散型随机变量的期望**

如果 $X$ 的分布律为：

$$
P(X=x_i)=p_i
$$

那么：

$$
\boxed{E(X)=\sum_i x_i p_i}
$$

这是最基本的期望计算公式。

更重要的是，我们经常需要计算随机变量的函数的期望。

假设：

$$
Y=g(X)
$$

那么：

$$
\boxed{E[g(X)]=\sum_i g(x_i)p_i}
$$

例如：

$$
E(X^2)=\sum_i x_i^2p_i
$$

$$
E\left(\frac{1}{X}\right) =\sum_i\frac{1}{x_i}p_i
$$

这里有一个非常重要的思想：

**计算函数的期望时，直接对原随机变量的取值进行函数变换，再乘以原来的概率即可。**

不需要先求出 $Y=g(X)$ 的分布。

## **3. 连续型随机变量的期望**

如果 $X$ 是连续型随机变量，概率密度为 $f_X(x)$，那么：

$$
\boxed{E(X)=\int_{-\infty}^{+\infty}xf_X(x)\,dx}
$$

对于函数：

$$
Y=g(X)
$$

有：

$$
\boxed{ E[g(X)]=\int_{-\infty}^{+\infty} g(x)f_X(x)\,dx }
$$

积分范围实际上只需要覆盖概率密度非零的区域。

例如，若：

$$
f_X(x)= \begin{cases} 2x,&0<x<1\\ 0,&\text{其他} \end{cases}
$$

那么：

$$
E(X)=\int_0^1x\cdot2x\,dx
$$

$$
=\int_0^1 2x^2\,dx =\frac23
$$

而：

$$
E(X^2)=\int_0^1x^2\cdot2x\,dx =\frac12
$$

这两个量后面计算方差时会用到。

## **4. 二维随机变量的期望**

这是作业第 9 题涉及的内容。

假设 $(X,Y)$ 的联合概率密度为：

f_{X,Y}(x,y)

那么：

$$
\boxed{ E[g(X,Y)] = \iint_D g(x,y)f_{X,Y}(x,y)\,dx\,dy }
$$

这里 $D$ 是联合密度非零的区域。

几个常用公式：

| 要计算的量            | 公式                                    |
| ---------------- | ------------------------------------- |
| $E(X)$       | $\iint_D xf(x,y)\,dxdy$        |
| $E(Y)$       | $\iint_D yf(x,y)\,dxdy$        |
| $E(XY)$      | $\iint_D xyf(x,y)\,dxdy$       |
| $E(X^2)$     | $\iint_D x^2f(x,y)\,dxdy$      |
| $E(Y^2)$     | $\iint_D y^2f(x,y)\,dxdy$      |
| $E(X^2+Y^2)$ | $\iint_D(x^2+y^2)f(x,y)\,dxdy$ |

**注意：计算二维随机变量的函数期望，直接使用联合密度即可，不需要先求边缘密度。**

### **具体看作业第 9 题**

题目给出：

$$
f(x,y)= \begin{cases} 12y^2,&0\leq y\leq x\leq1\\ 0,&\text{其他} \end{cases}
$$

要求：

E(X),E(Y),E(XY),E(X^2+Y^2)

首先理解积分区域：

$$
0\leq y\leq x\leq1
$$

它表示：

- $x$ 从 0 到 1；
- 固定一个 $x$，$y$ 从 0 到 $x$。

[Evaluate the double integral \\int \\int\_R (x^2 + xy) dA, where R is the triangle in the xy-plane having vertices at (0, 0), (1, 1), and (1, 0). |](https://images.openai.com/static-rsc-4/6lwA1nppS4V5DumfyO70yRF_gdaDYI46ScfJKb6Sh0__XyaLvNNLAgLUjoSriFn0hwgHTZWDqfxUZfFcYxCoS4jrd-x-gzcaro-azzXNRa_dTeMf_iOrQCkLh2MH6SvxJbZn5yETQsEA4weI6hggpSISZ5jAxG6ZC3jyxxqJYPA?purpose=inline) [Homework.Study.com](http://Homework.Study.com)

因此积分顺序为：

$$
\int_0^1\int_0^x(\cdots)\,dy\,dx
$$

例如计算 $E(X)$：

$$
E(X)=\int_0^1\int_0^x x\cdot12y^2\,dy\,dx
$$

先对 $y$ 积分：

$$
=\int_0^1 12x \left[\frac{y^3}{3}\right]_0^x dx
$$

$$
=\int_0^1 4x^4dx =\boxed{\frac45}
$$

你只需要记住一个规则：

**求哪个随机变量的期望，就在联合密度前面乘上对应的函数。**

这就是第 9 题的核心。

11.12-概率论与随机过程-第四次作业.pdf

## **5. 期望的线性性质**

这个性质非常重要，几乎每道题都会用到。

$$
\boxed{E(aX+bY+c)=aE(X)+bE(Y)+c}
$$

特别地：

$$
E(X+Y)=E(X)+E(Y)
$$

$$
E(X-Y)=E(X)-E(Y)
$$

$$
E(X^2+Y^2)=E(X^2)+E(Y^2)
$$

**期望具有线性性，不要求** $X,Y$ **独立。**

但需要特别区分：

$$
E(XY)\neq E(X)E(Y)
$$

一般情况下不成立。

当 $X,Y$ 独立时，才有：

$$
\boxed{E(XY)=E(X)E(Y)}
$$

# **二、方差与标准差**

作业第 19、26、27 题都会用到方差。

## **1. 方差是什么？**

数学期望描述随机变量的平均水平。

方差（Variance）描述随机变量取值围绕期望的离散程度。

定义：

$$
\boxed{D(X)=E[(X-E(X))^2]}
$$

展开：

$$
D(X)=E[X^2-2XE(X)+E(X)^2]
$$

利用期望的线性性质：

$$
\boxed{D(X)=E(X^2)-[E(X)]^2}
$$

这是考试中最常用的方差计算公式。

你需要记住：

$$
\boxed{\text{方差}=\text{二阶矩}-\text{一阶矩的平方}}
$$

其中：

- $E(X)$：一阶原点矩；
- $E(X^2)$：二阶原点矩；
- $D(X)$：方差。

## **2. 方差的计算例子**

沿用前面的随机变量：

$$
f_X(x)=2x,\quad 0<x<1
$$

我们已经得到：

$$
E(X)=\frac23
$$

$$
E(X^2)=\frac12
$$

因此：

$$
D(X)=\frac12-\left(\frac23\right)^2
$$

$$
=\boxed{\frac1{18}}
$$

标准差：

$$
\boxed{\sigma_X=\sqrt{D(X)}}
$$

所以：

$$
\sigma_X=\frac{1}{3\sqrt2}
$$

标准差和随机变量具有相同的量纲，而方差具有量纲的平方。

## **3. 常见方差性质**

$$
D(X+c)=D(X)
$$

$$
D(aX)=a^2D(X)
$$

$$
\boxed{D(aX+b)=a^2D(X)}
$$

如果 $X,Y$ 独立：

$$
\boxed{D(X+Y)=D(X)+D(Y)}
$$

$$
\boxed{D(X-Y)=D(X)+D(Y)}
$$

注意这里为什么是加号？

因为方差中系数需要平方：

$$
D(aX+bY) =a^2D(X)+b^2D(Y)
$$

独立时才可以直接使用这个简化形式。

一般情况还需要协方差，下面会讲。

# **三、指示变量与数学期望**

这是第 14 题的核心知识点，也是组合概率题中非常常见的技巧。

## **1. 什么是指示变量？**

假设有一个事件 $A$。

定义随机变量：

$$
I_A= \begin{cases} 1,&A\text{发生}\\ 0,&A\text{不发生} \end{cases}
$$

这个随机变量叫作事件 $A$ 的指示变量。

它只有两个取值：

| 事件  | 指示变量 |
| --- | ---- |
| 发生  | 1    |
| 不发生 | 0    |

那么：

$$
E(I_A)=1\cdot P(A)+0\cdot P(A^c)
$$

因此：

$$
\boxed{E(I_A)=P(A)}
$$

这是指示变量最重要的性质。

## **2. 为什么要引入指示变量？**

考虑作业第 14 题：

有 $n$ 封不同的信和 $n$ 个信封，随机配对，求正确配对的信件数量 $X$ 的期望和方差。

直接研究 $X$ 的分布非常麻烦。

因为你需要考虑：

- 恰好有 0 封配对正确；
- 恰好有 1 封配对正确；
- 恰好有 2 封配对正确；
- ……

这涉及错排问题。

但我们可以换一种思路。

定义：

$$
I_i= \begin{cases} 1,&\text{第 }i\text{ 封信配对正确}\\ 0,&\text{否则} \end{cases}
$$

那么正确配对的总数量就是：

$$
\boxed{X=\sum_{i=1}^n I_i}
$$

对两边取期望：

$$
E(X)=\sum_{i=1}^n E(I_i)
$$

由于：

$$
P(I_i=1)=\frac1n
$$

所以：

$$
E(X)=n\cdot\frac1n =\boxed{1}
$$

这就是指示变量的威力：

**把一个复杂的计数随机变量，拆成多个简单的 0-1 随机变量。**

而且它们不需要相互独立，期望的线性性仍然成立。

11.12-概率论与随机过程-第四次作业.pdf

# **四、协方差与相关系数**

这是这次作业的第二个重点。

## **1. 为什么需要协方差？**

前面我们已经知道：

$$
D(X)=E[(X-E(X))^2]
$$

它衡量一个随机变量自身的波动。

现在有两个随机变量 $X,Y$，我们想知道：

**当** $X$ **偏离自己的期望时，**$Y$ **是否也倾向于偏离自己的期望？**

这就需要协方差（Covariance）。

定义：

$$
\boxed{ \operatorname{Cov}(X,Y) =E[(X-E(X))(Y-E(Y))] }
$$

展开后：

$$
\boxed{ \operatorname{Cov}(X,Y) =E(XY)-E(X)E(Y) }
$$

这是协方差最常用的计算公式。

## **2. 协方差的几何直觉**

**正协方差**

Cov(X,Y) ＞ 0

[Lesson 9 — Correlation | High School Statistics Textbook](https://images.openai.com/static-rsc-4/8c3HCxHSR70HTYUFOxq03PqwxJbZ7HHeOXun7DKrsyHj6cX7eyClolBbjzxhGGOjyvrpWMNJzhxneejNbIzEpa92saV7ZhZE01m8AlzPq85eO2ez8-SwedUr0S2c0PXkrTqj7w-xRsmCcyxsTP5WtGX_DkfWrZ92gu5l96_0iX4?purpose=inline)

当 $X$ 大于自身均值时，$Y$ 通常也倾向于大于自身均值。

**负协方差**

Cov(X,Y) ＜ 0

[Scatterplot showing negative correlation.](https://images.openai.com/static-rsc-4/rYRY4GQBsB7M-y2H0El8mV_bt1oO4e8Mg26EaLBElx6S5Wm7mxoVfvK-j8ebgSap2BNHr7q7P1zFOpWOS070azdXTLkjr8tsc3qnqZnQMsUd1ipLVjspuvhE6dVFqZ4GmQGWc7H2KCYS9ODsuMhJsqxfYisOJivaU6nzxS0ijZZ3ECTYalE8M0FuT1N_Nu-_?purpose=inline)

当 $X$ 大于自身均值时，$Y$ 通常倾向于小于自身均值。

**零协方差**

$$
Cov(X,Y) = 0
$$

[Covariance vs. Correlation: What’s the Difference and Why It Matters | by Suruchi | Medium](https://images.openai.com/static-rsc-4/SQpgxMG-gzpT7e6NnaEG4_dBtElp6UlqHX3yyzPJAEDZE8MyXgxKUaIVJHmKS5gGr7nhzEZztH5jG8KqWBsKKrClPtFz85AI80ABdiU72fYTaf3PJaALdb_GHsnELHIK2dNdiB7XpXtxlyoF9XmBCeg8BYtWzztsaRUrX2LS25Y?purpose=inline)

两个随机变量没有线性相关性。

## **3. 协方差的性质**

$$
\operatorname{Cov}(X,X)=D(X)
$$

$$
\operatorname{Cov}(X,Y)=\operatorname{Cov}(Y,X)
$$

$$
\operatorname{Cov}(X,c)=0
$$

最重要的是双线性性质：

$$
\boxed{ \begin{aligned} &\operatorname{Cov}(aX+bY,cZ+dW)\\ ={}&ac\operatorname{Cov}(X,Z) +ad\operatorname{Cov}(X,W)\\ &+bc\operatorname{Cov}(Y,Z) +bd\operatorname{Cov}(Y,W) \end{aligned} }
$$

例如：

\operatorname{Cov}(X+Y,X-Y)

展开：

$$
=D(X)-D(Y)
$$

因为：

$$
\operatorname{Cov}(X,Y) -\operatorname{Cov}(Y,X)=0
$$

## **4. 相关系数**

协方差有一个问题：它的数值受到随机变量量纲和尺度影响。

因此我们需要进行标准化。

定义相关系数：

$$
\boxed{ \rho_{XY} = \frac{\operatorname{Cov}(X,Y)} {\sqrt{D(X)}\sqrt{D(Y)}} }
$$

其中：

-1\leq\rho_{XY}\leq1

解释：

| 相关系数                   | 含义      |
| ---------------------- | ------- |
| $\rho=1$          | 完全正线性相关 |
| $\rho=-1$         | 完全负线性相关 |
| $\rho=0$          | 不相关     |
| $0<\rho<1$  | 正相关     |
| $-1<\rho<0$ | 负相关     |

当两个随机变量方差都大于零时，相关系数才有定义。

## **5. 不相关与独立的关系**

这个知识点在作业第 26、27 题中反复出现。

你必须区分：

- 独立：两个随机变量的取值互不影响；
- 不相关：两个随机变量的线性相关程度为零。

它们之间的关系：

$$
\boxed{\text{独立}\Rightarrow\text{不相关}}
$$

在二阶矩存在的前提下成立。

但是：

$$
\boxed{\text{不相关}\not\Rightarrow\text{独立}}
$$

这是非常重要的考试考点。

### **例子：作业第 26 题**

设：

$$
Y=|X|
$$

那么显然，$Y$ 完全由 $X$ 决定，因此两者不独立。

但是题目中 $X$ 的密度关于 0 对称：

$$
f_X(x)=\frac12e^{-|x|}
$$

因此：

$$
E(X)=0
$$

又因为：

$$
E(X|X|)=0
$$

所以：

$$
\operatorname{Cov}(X,|X|) =E(X|X|)-E(X)E(|X|) =0
$$

也就是说：

$$
\boxed{X\text{ 与 }|X|\text{ 不相关，但不独立}}
$$

这是一个非常典型的反例。

### **作业第 27 题：如何判断离散型随机变量是否独立？**

如果给出联合分布表：

$$
P(X=x_i,Y=y_j)
$$

判断独立，需要验证：

$$
\boxed{ P(X=x_i,Y=y_j) =P(X=x_i)P(Y=y_j) }
$$

对所有可能取值组合都成立。

只要找到一个组合不满足，就可以证明不独立。

作业第 27 题就是通过：

$$
P(X=0,Y=0)=0
$$

但：

$$
P(X=0)P(Y=0)=\frac1{16}
$$

证明不独立。

与此同时，它的协方差为零，所以不相关但不独立。

11.12-概率论与随机过程-第四次作业.pdf

# **五、随机变量的线性组合与正态分布**

这是第 22、28 题的主要知识点。

## **1. 正态分布的基本概念**

正态分布：

$$
X\sim N(\mu,\sigma^2)
$$

其中：

- $\mu$：数学期望；
- $\sigma^2$：方差；
- $\sigma$：标准差。

对应密度：

$$
f_X(x)= \frac{1}{\sqrt{2\pi}\sigma} e^{-\frac{(x-\mu)^2}{2\sigma^2}}
$$

你需要熟悉标准正态分布：

Z\sim N(0,1)

标准化公式：

$$
\boxed{Z=\frac{X-\mu}{\sigma}}
$$

标准正态分布函数记为：

$$
\Phi(z)=P(Z\leq z)
$$

常用概率：

$$
P(Z>a)=1-\Phi(a)
$$

$$
P(Z<a)=\Phi(a)
$$

## **2. 两个独立正态随机变量的线性组合**

假设：

$$
X\sim N(\mu_1,\sigma_1^2)
$$

$$
Y\sim N(\mu_2,\sigma_2^2)
$$

并且 $X,Y$ 相互独立。

定义：

$$
Z=aX+bY+c
$$

那么：

$$
\boxed{Z\sim N(\mu_Z,\sigma_Z^2)}
$$

其中：

$$
\boxed{\mu_Z=a\mu_1+b\mu_2+c}
$$

$$
\boxed{\sigma_Z^2=a^2\sigma_1^2+b^2\sigma_2^2}
$$

注意两个地方：

1. 均值按照原系数计算；
2. 方差按照系数的平方计算。

### **举例：作业第 22 题**

给出：

X\sim N(720,30^2)

Y\sim N(640,25^2)

且相互独立。

求：

$$
Z_1=2X+Y
$$

那么：

$$
E(Z_1)=2\times720+640=2080
$$

$$
D(Z_1)=2^2\times30^2+25^2
$$

$$
=4225=65^2
$$

所以：

$$
\boxed{Z_1\sim N(2080,65^2)}
$$

再看：

$$
Z_2=X-Y
$$

$$
E(Z_2)=720-640=80
$$

$$
D(Z_2)=30^2+25^2=1525
$$

所以：

$$
\boxed{Z_2\sim N(80,1525)}
$$

## **3. 如何利用正态分布求概率？**

例如：

$$
P(X>Y)
$$

不要直接考虑二维区域积分。

令：

$$
Z=X-Y
$$

那么：

$$
P(X>Y)=P(Z>0)
$$

已知：

Z\sim N(80,1525)

标准化：

$$
P(Z>0) =P\left(\frac{Z-80}{\sqrt{1525}}> \frac{-80}{\sqrt{1525}}\right)
$$

因此：

$$
\boxed{ P(X>Y)=\Phi\left(\frac{80}{\sqrt{1525}}\right) }
$$

同理：

X+Y\sim N(1360,1525)

所以：

$$
P(X+Y>1400) = 1-\Phi\left(\frac{40}{\sqrt{1525}}\right)
$$

**这一类题目的核心技巧：将两个随机变量的不等式转化成一个随机变量的线性组合，再使用正态分布。**

# **六、两个线性组合的相关系数**

作业第 28 题考察的是协方差的双线性性质。

设：

$$
X,Y\text{ 独立}
$$

并且：

$$
D(X)=D(Y)=\sigma^2
$$

定义：

$$
\xi=\alpha X+\beta Y
$$

$$
\eta=\alpha X-\beta Y
$$

我们想计算：

$$
\rho_{\xi\eta}
$$

首先求方差：

$$
D(\xi)=\alpha^2\sigma^2+\beta^2\sigma^2
$$

$$
D(\eta)=\alpha^2\sigma^2+\beta^2\sigma^2
$$

再求协方差：

$$
\begin{aligned} \operatorname{Cov}(\xi,\eta) ={}&\operatorname{Cov}(\alpha X+\beta Y, \alpha X-\beta Y)\\ ={}&\alpha^2D(X)-\beta^2D(Y)\\ ={}&(\alpha^2-\beta^2)\sigma^2 \end{aligned}
$$

最后：

$$
\rho_{\xi\eta} = \frac{\operatorname{Cov}(\xi,\eta)} {\sqrt{D(\xi)D(\eta)}}
$$

得到：

$$
\boxed{ \rho_{\xi\eta} = \frac{\alpha^2-\beta^2} {\alpha^2+\beta^2} }
$$

这个题型的核心是：

**先展开协方差，再代入相关系数定义。**

不要直接尝试寻找 $\xi,\eta$ 的联合分布。

11.12-概率论与随机过程-第四次作业.pdf

# **七、最大值与最小值的期望**

作业第 34 题涉及一个比较特殊的知识点。

假设：

$$
X,Y\overset{i.i.d.}{\sim}N(a,\sigma^2)
$$

要求：

E(\max(X,Y))

以及：

E(\min(X,Y))

## **1. 一个非常有用的恒等式**

对于任意两个实数 $x,y$：

$$
\boxed{ \max(x,y)=\frac{x+y+|x-y|}{2} }
$$

$$
\boxed{ \min(x,y)=\frac{x+y-|x-y|}{2} }
$$

这两个公式建议直接记下来。

将随机变量代入：

$$
E(\max(X,Y)) = \frac{E(X)+E(Y)+E(|X-Y|)}{2}
$$

因此问题转化成：

E(|X-Y|)

## **2. 利用正态分布的性质**

由于 $X,Y$ 独立：

$$
W=X-Y
$$

仍然服从正态分布：

$$
W\sim N(0,2\sigma^2)
$$

它的密度为：

$$
f_W(w)= \frac{1}{2\sigma\sqrt{\pi}} e^{-\frac{w^2}{4\sigma^2}}
$$

现在计算：

$$
E(|W|) = \int_{-\infty}^{+\infty}|w|f_W(w)\,dw
$$

由于密度关于 0 对称：

$$
=2\int_0^\infty wf_W(w)\,dw
$$

代入：

$$
=\frac1{\sigma\sqrt{\pi}} \int_0^\infty we^{-\frac{w^2}{4\sigma^2}}dw
$$

令：

$$
t=\frac{w^2}{4\sigma^2}
$$

则：

$$
w\,dw=2\sigma^2dt
$$

所以：

$$
E(|W|) = \frac{2\sigma^2}{\sigma\sqrt{\pi}} \int_0^\infty e^{-t}dt
$$

最终：

$$
\boxed{E(|W|)=\frac{2\sigma}{\sqrt{\pi}}}
$$

## **3. 得到最终结果**

因为：

$$
E(X)=E(Y)=a
$$

所以：

$$
E(\max(X,Y)) = \frac{2a+\frac{2\sigma}{\sqrt{\pi}}}{2}
$$

$$
\boxed{ E(\max(X,Y))=a+\frac{\sigma}{\sqrt{\pi}} }
$$

同理：

$$
\boxed{ E(\min(X,Y))=a-\frac{\sigma}{\sqrt{\pi}} }
$$

这道题最值得掌握的是：

- max/min 与绝对值之间的恒等式；
- 独立正态变量的差仍然服从正态分布；
- 对称密度下可以利用偶函数简化积分。

11.12-概率论与随机过程-第四次作业.pdf

# **八、二维正态分布的第五个参数：相关系数**

最后的补充证明比较偏理论。

这部分对应老师额外布置的证明题。

## **1. 二维正态分布**

二维正态分布通常写成：

$$
(X,Y)\sim N(\mu_1,\mu_2, \sigma_1^2,\sigma_2^2,\rho)
$$

其中包含五个参数：

| 参数                 | 含义          |
| ------------------ | ----------- |
| $\mu_1$      | $X$ 的期望 |
| $\mu_2$      | $Y$ 的期望 |
| $\sigma_1^2$ | $X$ 的方差 |
| $\sigma_2^2$ | $Y$ 的方差 |
| $\rho$        | 两个随机变量的相关系数 |

老师要求证明：

$$
\boxed{\rho_{XY}=\rho}
$$

即联合密度中的第五个参数确实是两个随机变量的相关系数。

## **2. 先进行标准化**

令：

$$
Z=\frac{X-\mu_1}{\sigma_1}
$$

$$
W=\frac{Y-\mu_2}{\sigma_2}
$$

这样两个随机变量都变成了标准化变量。

其联合密度为：

$$
f_{Z,W}(z,w)= \frac{1}{2\pi\sqrt{1-\rho^2}} \exp\left( -\frac{z^2-2\rho zw+w^2} {2(1-\rho^2)} \right)
$$

可以看到，两个变量之间的关系由 $\rho$ 控制。

## **3. 进行变量变换**

定义：

$$
U=Z
$$

$$
V=\frac{W-\rho Z}{\sqrt{1-\rho^2}}
$$

反过来：

$$
Z=U
$$

$$
W=\rho U+\sqrt{1-\rho^2}V
$$

通过变量变换公式：

$$
f_{U,V}(u,v) = f_{Z,W}(z(u,v),w(u,v))|J|
$$

其中雅可比行列式：

|J|=\sqrt{1-\rho^2}

代入并化简：

$$
\boxed{ f_{U,V}(u,v) = \frac1{2\pi}e^{-\frac{u^2+v^2}{2}} }
$$

拆开：

$$
f_{U,V}(u,v) = \frac1{\sqrt{2\pi}}e^{-u^2/2} \cdot \frac1{\sqrt{2\pi}}e^{-v^2/2}
$$

因此：

U,V\overset{ind}{\sim}N(0,1)

## **4. 计算原随机变量的协方差**

根据反变换：

$$
X=\mu_1+\sigma_1U
$$

$$
Y=\mu_2+\sigma_2 (\rho U+\sqrt{1-\rho^2}V)
$$

我们知道：

$$
E(U)=E(V)=0
$$

$$
D(U)=D(V)=1
$$

$$
E(UV)=0
$$

因此：

$$
E(X)=\mu_1
$$

$$
E(Y)=\mu_2
$$

以及：

$$
D(X)=\sigma_1^2
$$

$$
D(Y)=\sigma_2^2
$$

现在计算协方差：

$$
\begin{aligned} \operatorname{Cov}(X,Y) &=\sigma_1\sigma_2 E[U(\rho U+\sqrt{1-\rho^2}V)]\\ &=\sigma_1\sigma_2 (\rho E(U^2)+\sqrt{1-\rho^2}E(UV))\\ &=\rho\sigma_1\sigma_2 \end{aligned}
$$

代入相关系数定义：

$$
\rho_{XY} = \frac{\operatorname{Cov}(X,Y)} {\sigma_1\sigma_2}
$$

所以：

$$
\boxed{\rho_{XY}=\rho}
$$

证明完成。

11.12-概率论与随机过程-第四次作业.pdf

# **九、这次作业的知识点总表**

我把所有内容按照重要程度整理一下。

| 知识点     | 需要掌握的内容              | 对应题目        |
| ------- | -------------------- | ----------- |
| 数学期望    | 离散、连续、二维函数期望         | 9、19、26、27  |
| 期望性质    | 线性性、函数期望             | 9、14、19     |
| 指示变量    | 事件转化为 0-1 随机变量       | 14          |
| 方差      | 二阶矩减去均值平方            | 14、19、26、27 |
| 协方差     | $E(XY)-E(X)E(Y)$ | 26、27、28    |
| 相关系数    | 协方差标准化               | 26、27、28    |
| 独立性与不相关 | 两者的关系及反例             | 26、27       |
| 正态线性组合  | 均值和方差计算              | 22、28、34    |
| 正态分布标准化 | 利用 $\Phi$ 求概率   | 22          |
| 最大值与最小值 | 绝对值恒等式、正态积分          | 34          |
| 二维正态    | 参数含义、变量变换、雅可比        | 补充证明        |

# **十、建议你的学习顺序**

不要按照题目编号学习，我建议按照下面的顺序：

## **本次作业学习路线**

1. **第一阶段：期望**
   - 离散型期望
   - 连续型期望
   - 二维随机变量函数期望
   - 期望的线性性质
2. **第二阶段：方差**
   - 二阶矩
   - 方差计算
   - 标准差
   - 指示变量求期望和方差
3. **第三阶段：协方差与相关系数**
   - 协方差计算
   - 协方差展开
   - 相关系数
   - 独立与不相关
4. **第四阶段：正态分布**
   - 正态分布的线性组合
   - 标准化
   - 利用标准正态分布求概率
   - 最大值与最小值的期望
5. **第五阶段：二维正态**
   - 二维正态密度
   - 变量变换
   - 雅可比行列式
   - 相关系数参数的证明
