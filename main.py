import tkinter, pywinstyles, sv_ttk, ctypes, psutil, os, sys
import tkinter.ttk as Widgets
import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox
from platform import system
from ctypes import wintypes

# # # Injection Code (kinda trash) # # #
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

PROCESS_ALL_ACCESS = 0x001F0FFF
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_READWRITE = 0x04

kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE

kernel32.VirtualAllocEx.argtypes = [wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
kernel32.VirtualAllocEx.restype = wintypes.LPVOID

kernel32.WriteProcessMemory.argtypes = [wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
kernel32.WriteProcessMemory.restype = wintypes.BOOL

kernel32.CreateRemoteThread.argtypes = [wintypes.HANDLE, wintypes.LPVOID, ctypes.c_size_t, wintypes.LPVOID, wintypes.LPVOID, wintypes.DWORD, wintypes.LPDWORD]
kernel32.CreateRemoteThread.restype = wintypes.HANDLE

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

def get_proc_id(proc_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == proc_name.lower():
            return proc.info['pid']
    return None

def perform_injection(proc_id, dll_path):
    h_proc = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, proc_id)
    
    if h_proc and h_proc != 0:
        dll_path_unicode = ctypes.create_unicode_buffer(dll_path)
        path_len = ctypes.sizeof(dll_path_unicode)
        
        alloc_mem = kernel32.VirtualAllocEx(h_proc, None, path_len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)
        
        if alloc_mem:
            bytes_written = ctypes.c_size_t(0)
            kernel32.WriteProcessMemory(h_proc, alloc_mem, ctypes.byref(dll_path_unicode), path_len, ctypes.byref(bytes_written))
            
            h_kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            load_library_addr = ctypes.cast(h_kernel32.LoadLibraryW, ctypes.c_void_p).value
            
            thread_id = wintypes.DWORD(0)
            h_thread = kernel32.CreateRemoteThread(h_proc, None, 0, ctypes.c_void_p(load_library_addr), alloc_mem, 0, ctypes.byref(thread_id))
            
            if h_thread:
                kernel32.CloseHandle(h_thread)
                return f"Injected! | PID: {proc_id}"
            else:
                error = ctypes.get_last_error()
                return f"Error in CreateRemoteThread: {error}"
        else:
            error = ctypes.get_last_error()
            return f"Error in VirtualAllocEx: {error}"
    
    if h_proc:
        kernel32.CloseHandle(h_proc)
    
    return 0
# # # Injection Code End # # #

# # # GUI Code # # #
def selctfile():
    file_path = FileDialog.askopenfilename(
        title="Select DLL",
        filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
    )
    if file_path: # Not canceled
        filetext.set(file_path)

def inject():
    if get_proc_id(procname.get()) is None:
        MessageBox.showerror("Error", "Process not found.")
        return
    MessageBox.showinfo("Result", perform_injection(get_proc_id(procname.get()), filetext.get()))

def GetResource(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller Temp Folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# # # GUI Code End # # #

app = tkinter.Tk()
app.geometry("250x150")
app.title("DLL Injector")
app.iconbitmap(GetResource("icon.ico"))
app.resizable(False, False)

if __name__ != "__main__":
    MessageBox.showerror("Error", "Run program as main.")
    exit(1)

if system() != "Windows":
    MessageBox.showerror("Error", "Run program as Windows.")
    exit(1)

filetext = tkinter.StringVar()
filetext.set("Example.dll")

proctext = tkinter.StringVar()
proctext.set("Example.exe")

procname = Widgets.Entry(app, textvariable=proctext)
procname.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="we")

filename = Widgets.Entry(app, textvariable=filetext, state="readonly")
filename.grid(row=1, column=0, columnspan=2, padx=10, pady=(5, 5), sticky="we")

select = Widgets.Button(app, text="Select DLL", command=selctfile)
select.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="we")

inject_btn = Widgets.Button(app, text="Inject DLL", command=inject)
inject_btn.grid(row=2, column=1, padx=(5, 10), pady=10, sticky="we")

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

sv_ttk.set_theme("dark")

pywinstyles.apply_style(app, "acrylic")
pywinstyles.change_border_color(app, color="#8d8d8d")

app.mainloop()