import os
import shutil
import sys
import re
import json
import random
import string
import winreg
import ctypes
from utils import Logger


class ScriptBuilder:
    def __init__(self, intents: os.PathLike = 'intents.json'):
        self.intents = intents
        self.logger = Logger()

        if not os.path.exists(self.intents):
            self.logger.colorp(Logger.Level.FATAL, f"Could not find intents file: {self.intents}")
        
        self.logger.colorp(Logger.Level.SUCCESS, f"Found intents file: {self.intents}")

        self.build()


    def load_intents(self) -> dict:
        with open(self.intents, 'r') as f:
            try:
                contents = json.load(f)
                self.logger.colorp(Logger.Level.SUCCESS, f"Loaded intents file: {self.intents}")
                return contents
            except Exception as e:
                self.logger.colorp(Logger.Level.WARNING, f"Could not load intents file: {self.intents}")
                self.logger.colorp(Logger.Level.FATAL, f"Error: {e}")
                sys.exit(1)
    

    def check_object(self, object) -> bool:
        return os.path.isfile(object) or os.path.isdir(object)


    def modify_system_path(self, new_path):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_WRITE
            )
            current_path = winreg.QueryValueEx(key, "Path")[0]
            if new_path not in current_path:
                new_path = f"{current_path};{new_path}"
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                winreg.CloseKey(key)
                self.logger.colorp(Logger.Level.SUCCESS, f"Successfully modified system PATH variable.")
            else:
                winreg.CloseKey(key)
                self.logger.colorp(Logger.Level.WARNING, f"The provided path is already in the system PATH variable.")
        except Exception as e:
            self.logger.colorp(Logger.Level.FATAL, f"Could not modify system PATH variable: {e}")
            sys.exit(1)


    def build(self):
        #########################################################################################################
        # Load Intents
        #########################################################################################################


        self.logger.colorp(Logger.Level.INFO, "Loading Intents...")
        intents: dict = self.load_intents()
        included = []

        
        driver = intents['storage']['driver']
        # Remove all special characters from the drive name
        if re.search(r'[:\\/]', driver):
            self.logger.colorp(Logger.Level.WARNING, f"Found special characters in drive name: {driver}")
            drive = re.sub(r'[:\\/]', '', driver) + ":\\"
        else:
            drive = driver + ":\\"

        self.logger.colorp(Logger.Level.INFO, "Checking Drive...")
        
        if self.check_object(drive):
            self.logger.colorp(Logger.Level.SUCCESS, f"Found Drive: {drive}")
        else:
            self.logger.colorp(Logger.Level.FATAL, f"Could not find Drive: {drive}")
            sys.exit(1)
        
        main_script = intents['script']['mainScript']
        self.logger.colorp(Logger.Level.INFO, "Checking Main Script...")
        
        if self.check_object(main_script):
            self.logger.colorp(Logger.Level.SUCCESS, f"Found Main Script: {main_script}")
            included.append(main_script)
        else:
            self.logger.colorp(Logger.Level.FATAL, f"Could not find Main Script")
            sys.exit(1)
        
        project_dir = os.path.dirname(os.path.realpath(main_script))

        self.logger.colorp(Logger.Level.INFO, "Finding other included files...")
        included_files = intents['script']['include']

        if len(included_files) == 0:
            self.logger.colorp(Logger.Level.WARNING, "No included files found.")
        else:
            files_found = 0
            total_files = 0
            for file in included_files:
                if self.check_object(os.path.join(project_dir, file)):
                    self.logger.colorp(Logger.Level.SUCCESS, f"Found included file: {file}")
                    included.append(os.path.join(project_dir, file))
                    files_found += 1
                else:
                    self.logger.colorp(Logger.Level.WARNING, f"Could not find included file: {file}")
                total_files += 1
            
            self.logger.colorp(Logger.Level.INFO, f"Found {files_found} out of {total_files} included files.")
        
        self.logger.colorp(Logger.Level.INFO, "Getting Commands...")
        commands: str = intents['command']
        

        #########################################################################################################
        # Build Script
        #########################################################################################################
        
        
        self.logger.colorp(Logger.Level.INFO, "Building Script...")

        self.logger.colorp(Logger.Level.INFO, "Creating Script Storage...")
        script_storage = os.path.join(drive, intents['storage']['scriptStorage'])

        # Create the script storage if it doesn't exist
        if not os.path.exists(script_storage):
            try:
                os.mkdir(script_storage)
                self.logger.colorp(Logger.Level.SUCCESS, f"Created Script Storage.")
            except Exception as e:
                self.logger.colorp(Logger.Level.FATAL, f"Could not create Script Storage: {e}")
                sys.exit(1)
        else:
            self.logger.colorp(Logger.Level.WARNING, "Script Storage already exists.")
        
        self.logger.colorp(Logger.Level.INFO, "Copying contents to Script Storage...")

        # Create a organized subfolder
        final_dest = os.path.join(script_storage, os.path.basename(project_dir).replace(' ', '_').lower().replace('.py', ''))
        
        if not os.path.exists(final_dest):
            os.mkdir(final_dest)


        # Copy all the files to the final destination
        for file in included:
            try:
                self.logger.colorp(Logger.Level.INFO, f"Copying {file} to {final_dest}...")
                # Extract the relative path from the project directory to the included file
                relative_path = os.path.relpath(file, project_dir)
                # Create the subdirectories in the final destination if they don't exist
                subdirectories = os.path.dirname(relative_path)
                if subdirectories:
                    os.makedirs(os.path.join(final_dest, subdirectories), exist_ok=True)
                # Copy the file to the final destination
                destination_file = os.path.join(final_dest, relative_path)
                shutil.copy2(file, destination_file)
            except Exception as e:
                self.logger.colorp(Logger.Level.WARNING, f"Could not copy {file} to {final_dest}: {e}")
        
        self.logger.colorp(Logger.Level.SUCCESS, "Finished copying files.")
        self.logger.colorp(Logger.Level.INFO, "Editing Environment Variables...")

        # Because windows is stupid, create a new BAT file with the name of the script
        # and then run that file instead of the script itself.
        
        # Rename original script, no overlap
        random_name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        os.rename(os.path.join(final_dest, os.path.basename(main_script)), os.path.join(final_dest, random_name + '.py'))

        # Create new BAT file
        with open(os.path.join(final_dest, os.path.basename(main_script).replace('.py', '.bat')), 'w') as f:
            f.write(f"{commands.replace(os.path.basename(main_script), random_name + '.py')}")
            

        #########################################################################################################
        # Modify System Path
        #########################################################################################################

        # try:
        #     # Get sys path
        #     system_path_buffer = ctypes.create_unicode_buffer(1024)
        #     ctypes.windll.kernel32.GetEnvironmentVariableW('Path', system_path_buffer, 1024)
        #     path = system_path_buffer.value
        # except Exception as e:
        #     self.logger.colorp(Logger.Level.FATAL, f"Could not get environment variables: {e}")
        #     sys.exit(1)
        # 
        # if final_dest not in path:
        #     try:
        #         # Add the final destination to the environment variables
        #         self.logger.colorp(Logger.Level.INFO, f"Adding {final_dest} to environment variables...")
        #         ctypes.windll.kernel32.SetEnvironmentVariableW('Path', f"{path};{final_dest}")
        #     except Exception as e:
        #         self.logger.colorp(Logger.Level.FATAL, f"Could not add {final_dest} to environment variables: {e}")
        #         sys.exit(1)

        self.modify_system_path(final_dest)
        
        self.logger.colorp(Logger.Level.SUCCESS, "Finished editing environment variables.")
        self.logger.colorp(Logger.Level.SUCCESS, "Finished building script.")


if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        ScriptBuilder()
    else:
        l = Logger()
        l.colorp(Logger.Level.FATAL, "Please run this script as an administrator.")