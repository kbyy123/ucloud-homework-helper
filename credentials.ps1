# Windows Credential Manager wrapper. Secrets stay in the user vault and process memory.
if (-not ('BuptHomeworkVault' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class BuptHomeworkVault {
    const string Target = "BUPT.HomeworkAssistant.Ucloud";
    [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
    struct Credential {
        public UInt32 Flags, Type;
        public string TargetName, Comment;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWritten;
        public UInt32 CredentialBlobSize;
        public IntPtr CredentialBlob;
        public UInt32 Persist, AttributeCount;
        public IntPtr Attributes;
        public string TargetAlias, UserName;
    }
    public sealed class Secret {
        public string UserName;
        public string Password;
    }
    [DllImport("advapi32.dll", EntryPoint="CredWriteW", CharSet=CharSet.Unicode, SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CredWrite(ref Credential credential, UInt32 flags);
    [DllImport("advapi32.dll", EntryPoint="CredReadW", CharSet=CharSet.Unicode, SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CredRead(string target, UInt32 type, UInt32 flags, out IntPtr credential);
    [DllImport("advapi32.dll", EntryPoint="CredDeleteW", CharSet=CharSet.Unicode, SetLastError=true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool CredDelete(string target, UInt32 type, UInt32 flags);
    [DllImport("advapi32.dll")] static extern void CredFree(IntPtr credential);
    public static bool Exists() {
        IntPtr ptr;
        if (!CredRead(Target, 1, 0, out ptr)) {
            int error=Marshal.GetLastWin32Error();
            if (error==1168) return false;
            throw new Win32Exception(error);
        }
        CredFree(ptr); return true;
    }
    public static void Save(string userName, string password) {
        if (String.IsNullOrWhiteSpace(userName) || String.IsNullOrEmpty(password)) throw new ArgumentException("Missing credentials");
        IntPtr blob=Marshal.StringToCoTaskMemUni(password);
        try {
            var credential=new Credential {
                Type=1, TargetName=Target, UserName=userName,
                Comment="BUPT local homework assistant: read-only campus login",
                CredentialBlobSize=(UInt32)(password.Length*2), CredentialBlob=blob, Persist=2
            };
            if (!CredWrite(ref credential,0)) throw new Win32Exception(Marshal.GetLastWin32Error());
        } finally { Marshal.ZeroFreeCoTaskMemUnicode(blob); }
    }
    public static Secret Read() {
        IntPtr ptr;
        if (!CredRead(Target,1,0,out ptr)) throw new Win32Exception(Marshal.GetLastWin32Error());
        try {
            Credential c=(Credential)Marshal.PtrToStructure(ptr,typeof(Credential));
            return new Secret { UserName=c.UserName, Password=Marshal.PtrToStringUni(c.CredentialBlob,(int)c.CredentialBlobSize/2) };
        } finally { CredFree(ptr); }
    }
    public static void Delete() {
        if (!CredDelete(Target,1,0)) {
            int error=Marshal.GetLastWin32Error();
            if (error!=1168) throw new Win32Exception(error);
        }
    }
}
'@
}
