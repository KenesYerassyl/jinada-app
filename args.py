import argparse  


class Args:  
    def __init__(self):  
        parser = argparse.ArgumentParser(description="Project Description")  
        
        parser.add_argument("-v", "--visualize", action="store_true", help="Enable visualization mode (default is False)")  
        self.args = parser.parse_args()  

    def __getattr__(self, attr):  
        return getattr(self.args, attr)  

args_instance = Args()