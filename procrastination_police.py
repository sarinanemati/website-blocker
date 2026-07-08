
import datetime
import time
import subprocess
import platform
import os
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import json
from pathlib import Path

class ChatbotBlocker:
    def __init__(self):
        self.work_start_hour = 9
        self.work_end_hour = 17
        
        self.distracting_websites = [
            'chatgpt.com', 
            'chat.openai.com', 
            'openai.com',
            'claude.ai', 
            'claude.com', 
            'anthropic.com',
            'deepseek.com', 
            'deepseek.ai', 
            'chat.deepseek.com',
            'gemini.google.com', 
            'gemini.com', 
            'ai.google.com',
            'grok.x.com', 
            'grok.com', 
            'x.ai',
            'character.ai', 
            'characterai.com',
            'bing.com', 
            'copilot.microsoft.com',
            'perplexity.ai', 
            'perplexity.com',
            'poe.com', 
            'poe.ai',
            'you.com', 
            'you.ai',
            'pi.ai', 
            'heypi.com',
            'youtube.com', 
            'twitter.com', 
            'x.com',
            'reddit.com', 
            'facebook.com', 
            'instagram.com',
            'tiktok.com', 
            'netflix.com', 
            'twitch.tv'
        ]
        
        self.os_type = platform.system()
        self.hosts_path = self.get_hosts_path()
        self.hosts_backup = self.hosts_path + '.backup'
        self.is_running = True
        
        self.blocked_count = 0
        self.stats_file = Path.home() / ".chatbot_blocker_stats.json"
        self.load_stats()
        
    def get_hosts_path(self):
        """Get the hosts file path based on OS"""
        if self.os_type == "Windows":
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:  
            return "/etc/hosts"
    
    def load_stats(self):
        """Load statistics from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_count = data.get('blocked_count', 0)
            except Exception as e:
                print(f" Could not load stats: {e}")
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump({'blocked_count': self.blocked_count}, f)
        except Exception as e:
            print(f" Could not save stats: {e}")
    
    def is_work_time(self):
        """Check if current time is within work hours"""
        now = datetime.datetime.now()
        current_hour = now.hour
        is_weekday = now.weekday() < 5
        return is_weekday and self.work_start_hour <= current_hour < self.work_end_hour
    
    def backup_hosts(self):
        """Create backup of hosts file"""
        try:
            if not os.path.exists(self.hosts_backup):
                with open(self.hosts_path, 'r') as src:
                    with open(self.hosts_backup, 'w') as dst:
                        dst.write(src.read())
                print(" Hosts file backup created")
                return True
            return True
        except Exception as e:
            print(f" Could not backup hosts: {e}")
            return False
    
    def restore_hosts(self):
        """Restore hosts file from backup"""
        try:
            if os.path.exists(self.hosts_backup):
                with open(self.hosts_backup, 'r') as src:
                    with open(self.hosts_path, 'w') as dst:
                        dst.write(src.read())
                print(" Hosts file restored")
                return True
            return False
        except Exception as e:
            print(f" Could not restore hosts: {e}")
            return False
    
    def block_websites(self, force=False):
        """Add entries to hosts file to block websites"""
        try:
            self.backup_hosts()
            
            with open(self.hosts_path, 'r') as f:
                content = f.read()
            
            blocked_entries = []
            for site in self.distracting_websites:
                entry = f"127.0.0.1 {site}"
                if entry not in content and f"0.0.0.0 {site}" not in content:
                    blocked_entries.append(entry)
            
            if not blocked_entries:
                print(" All websites already blocked")
                return True
            
            with open(self.hosts_path, 'a') as f:
                f.write("\n# === BLOCKED BY PROCRASTINATION POLICE ===\n")
                for entry in blocked_entries:
                    f.write(f"{entry}\n")
                    print(f" Blocked: {entry.split()[1]}")
                    self.blocked_count += 1
            
            self.save_stats()
            print(f" Total {len(blocked_entries)} websites blocked!")
            
            self.flush_dns()
            
            return True
            
        except PermissionError:
            print(" PERMISSION DENIED! Please run as Administrator.")
            return False
        except Exception as e:
            print(f" Error blocking websites: {e}")
            return False
    
    def flush_dns(self):
        """Flush DNS cache to make changes take effect immediately"""
        try:
            if self.os_type == "Windows":
                print(" Flushing DNS cache...")
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                print(" DNS cache flushed!")
            elif self.os_type == "Darwin":  
                print(" Flushing DNS cache...")
                subprocess.run(['sudo', 'dscacheutil', '-flushcache'], capture_output=True)
                subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], capture_output=True)
                print(" DNS cache flushed!")
            else:  
                print(" Flushing DNS cache...")
                subprocess.run(['sudo', 'systemctl', 'restart', 'systemd-resolved'], capture_output=True)
                print(" DNS cache flushed!")
        except Exception as e:
            print(f" Could not flush DNS: {e}")
            print(" You may need to restart your browser for changes to take effect.")
    
    def unblock_websites(self, force=False):
        """Remove blocked entries from hosts file"""
        try:
            if not os.path.exists(self.hosts_path):
                print(" Hosts file not found")
                return False
            
            with open(self.hosts_path, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            in_blocked_section = False
            removed_count = 0
            
            for line in lines:
                if "# === BLOCKED BY PROCRASTINATION POLICE ===" in line:
                    in_blocked_section = True
                    continue
                elif in_blocked_section and (line.strip() == "" or "127.0.0.1" in line or "0.0.0.0" in line):
                    removed_count += 1
                    continue
                else:
                    in_blocked_section = False
                    new_lines.append(line)
            
            with open(self.hosts_path, 'w') as f:
                f.writelines(new_lines)
            
            print(f" Unblocked {removed_count} websites")
            
            self.flush_dns()
            
            return True
            
        except PermissionError:
            print(" PERMISSION DENIED! Please run as Administrator.")
            return False
        except Exception as e:
            print(f" ! Error unblocking websites: {e}")
            return False
    
    def show_popup(self, title, message, icon='warning'):
        """Show warning popup"""
        def show():
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            if icon == 'warning':
                messagebox.showwarning(title, message)
            elif icon == 'info':
                messagebox.showinfo(title, message)
            else:
                messagebox.showinfo(title, message)
            
            root.destroy()
        
        thread = threading.Thread(target=show, daemon=True)
        thread.start()
    
    def check_and_block(self, force=False):
        """Check if it's work time and block websites"""
        if not force and not self.is_work_time():
            return False
        
        print(f" Blocking chatbots and distractions...")
        
        result = self.block_websites(force=force)
        
        if result:
            self.show_popup(
                " Chatbots Blocked!",
                f"AI Chatbots and distracting websites are blocked!\n\n"
                f"Blocked: {len(self.distracting_websites)} sites\n"
                f"Total blocked: {self.blocked_count}\n\n"
                "Focus on your work! ",
                'warning'
            )
        return result
    
    def run_continuous_monitoring(self, check_interval=30, force_block=False):
        """Run monitoring continuously"""
        print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║     CHATBOT POLICE - AI Site Blocker                              ║
╠═══════════════════════════════════════════════════════════════════╣
║   Work Hours: {self.work_start_hour:02d}:00 - {self.work_end_hour:02d}:00                                 
║   Mode: {'FORCE BLOCK' if force_block else 'Work Hours Only'}                         
║   Blocked Sites: {len(self.distracting_websites)} sites including AI chatbots               
║   Check Interval: {check_interval} seconds                                    
║   Press Ctrl+C to deactivate                                               
╚═══════════════════════════════════════════════════════════════════╝
        """)
        
        print("\n This will modify your hosts file to block websites.")
        response = input("Continue? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("Operation cancelled.")
            return
        
        self.check_and_block(force=force_block)
        
        try:
            while self.is_running:
                if force_block or self.is_work_time():
                    self.check_and_block(force=force_block)
                else:
                    self.unblock_websites()
                    print(" Outside work hours - Websites unblocked")
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n Deactivated.")
            if not force_block:
                print("Restoring hosts file...")
                self.unblock_websites()
            print(" Goodbye!")

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    """Main entry point with menu"""
    blocker = ChatbotBlocker()
    
    while True:
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║     CHATBOT BLOCKER - AI Website Control                          ║
╠═══════════════════════════════════════════════════════════════════╣
║   1.  Start blocking (work hours only)                      
║   2.  FORCE BLOCK ALL chatbots NOW (ignores work hours)    
║   3.  Unblock ALL chatbots                                 
║   4.  Show statistics                                      
║   5.  Configure work hours                                 
║   6.  List blocked websites                                
║   7.  Flush DNS cache                                     
║   8.  Exit                                                  
╚═══════════════════════════════════════════════════════════════════╝
        """)
        
        choice = input("Select option (1-8): ").strip()
        
        if choice == '1':
            blocker.run_continuous_monitoring(force_block=False)
        elif choice == '2':
            print("\n FORCE BLOCKING all chatbot websites...")
            print(" Ignoring work hours - blocking NOW!")
            result = blocker.block_websites(force=True)
            if result:
                blocker.show_popup(
                    " Chatbots Force Blocked!",
                    f"All {len(blocker.distracting_websites)} AI chatbots are now BLOCKED!\n\n"
                    "Changes should take effect immediately.\n"
                    "You may need to restart your browser.",
                    'warning'
                )
        elif choice == '3':
            print("\n Unblocking all websites...")
            blocker.unblock_websites()
            blocker.show_popup(
                " Unblocked!",
                "All websites are now unblocked.\n"
                "You can use AI chatbots again!",
                'info'
            )
        elif choice == '4':
            print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║   STATISTICS                                                      ║
╠═══════════════════════════════════════════════════════════════════╣
║   Total blocked sites: {blocker.blocked_count}                                    
║   Sites in blocklist: {len(blocker.distracting_websites)}                                    
║   Work hours: {blocker.work_start_hour:02d}:00 - {blocker.work_end_hour:02d}:00                       
║   OS: {blocker.os_type}                                            
╚═══════════════════════════════════════════════════════════════════╝
            """)
        elif choice == '5':
            try:
                start = input(f"Enter new start hour (0-23, current: {blocker.work_start_hour}): ")
                end = input(f"Enter new end hour (0-23, current: {blocker.work_end_hour}): ")
                blocker.work_start_hour = int(start)
                blocker.work_end_hour = int(end)
                print(f" Work hours set to {blocker.work_start_hour:02d}:00 - {blocker.work_end_hour:02d}:00")
            except ValueError:
                print(" Invalid input. Please enter numbers.")
        elif choice == '6':
            print("\n Blocked Websites:")
            print("-" * 50)
            for i, site in enumerate(blocker.distracting_websites, 1):
                print(f"{i:2d}. {site}")
            print("-" * 50)
            print(f"Total: {len(blocker.distracting_websites)} sites")
        elif choice == '7':
            print(" Flushing DNS cache...")
            blocker.flush_dns()
            print(" DNS cache flushed! Restart your browser for changes.")
        elif choice == '8':
            print("\n Goodbye!")
            break
        else:
            print(" ! Invalid choice. Please try again.")

if __name__ == "__main__":
    if platform.system() == "Windows":
        if not is_admin():
            print("=" * 70)
            print(" !  ADMINISTRATOR RIGHTS REQUIRED")
            print("=" * 70)
            print("\nThis program needs to modify your hosts file.")
            print("Please run as Administrator.\n")
            print("To run as Administrator:")
            print("1. Close this window")
            print("2. Right-click PowerShell/Command Prompt")
            print("3. Select 'Run as administrator'")
            print("4. Navigate to this folder and run again\n")
            input("Press Enter to exit...")
            sys.exit(1)
    
    main()
    