import argparse


class BaseCommand:
    name = None
    help = "Base command for dynotec CLI"
    description = None

    @property
    def default_name(self):
        return self.__class__.__name__.lower().replace("Command","")
    
    def add_parser(self, subparsers,parents:list[argparse.ArgumentParser]=[]):
        parser = subparsers.add_parser(
            self.name or self.default_name, 
            help=self.help,
            description=self.description or self.help,
            parents=parents)
        parser.set_defaults(main=self.main)
        self.setup_parser(parser)
        return parser
    
    def setup_parser(self, parser:argparse.ArgumentParser):
        """
        Override this method to add arguments to the parser.
        """
        pass

    def pre_parse_args(self, args: list[str]) -> list[str]:
        """
        Override this method to modify the arguments before parsing.
        """
        return args
        
    def main(self, ns:argparse.Namespace,rest_args)->None:
        raise NotImplementedError("Subclasses should implement this method")
    


