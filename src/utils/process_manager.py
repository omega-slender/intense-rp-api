import psutil, os

def kill_driver_processes() -> None:
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name']
            base_name = os.path.splitext(proc_name)[0]
            
            if base_name in ["chromedriver", "geckodriver", "msedgedriver", "uc_driver"]:
                print(f"Terminating process: {proc_name} (PID: {proc.info['pid']})")
                proc.terminate()
        
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue