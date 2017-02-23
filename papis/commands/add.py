from ..document import Document
import papis
import sys
import os
import re
import shutil
import string
import papis.utils
import papis.bibtex
from . import Command

class Add(Command):
    def init(self):
        """TODO: Docstring for init.

        :subparser: TODO
        :returns: TODO

        """
        # add parser
        add_parser = self.parser.add_parser("add",
                help="Add a document into a given library")
        add_parser.add_argument("document",
                help="Document file name",
                default="",
                nargs="?",
                action="store")
        add_parser.add_argument("-d", "--dir",
            help    = "Subfolder in the library",
            default = "",
            action  = "store"
        )
        add_parser.add_argument("--name",
            help    = "Name for the main folder of the document",
            default = "",
            action  = "store"
        )
        add_parser.add_argument("--from-bibtex",
            help    = "Parse information from a bibtex file",
            default = "",
            action  = "store"
        )
        add_parser.add_argument("--from-url",
            help    = "Get document and information from a given url, a parser must be implemented",
            default = "",
            action  = "store"
        )

    def main(self, config, args):
        """
        Main action if the command is triggered

        :config: User configuration
        :args: CLI user arguments
        :returns: TODO

        """
        documentsDir = os.path.expanduser(config[args.lib]["dir"])
        folderName = None
        self.logger.debug("Using directory %s"%documentsDir)
        if args.from_url:
            url = args.from_url
            service = getUrlService(url)
            try:
                serviceParser = eval("add_from_%s"%service)
            except:
                print("No add_from_%s function has been implemented, sorry"%service)
                sys.exit(1)
            documentPath, data = serviceParser(url)
        else:
            documentPath = args.document
            data  = papis.bibtex.bibtexToDict(args.from_bibtex) \
                    if args.from_bibtex else dict()
        m = re.match(r"^(.*)\.([a-zA-Z]*)$", os.path.basename(documentPath))
        extension    = m.group(2) if m else ""
        # Set foldername
        if not args.from_bibtex and not args.name:
            folderName   = m.group(1) if m else os.path.basename(documentPath)
        elif args.from_bibtex and not args.name:
            args.name = '$year-$author-$title'
        if folderName == None:
            folderName = folderName if not args.name else \
                                        string\
                                        .Template(args.name)\
                                        .safe_substitute(data)\
                                        .replace(" ","-")
        documentName    = "document."+extension
        endDocumentPath = os.path.join(documentsDir, args.dir, folderName, documentName )
        fullDirPath = os.path.join(documentsDir, args.dir,  folderName)
        ######
        data["file"] = documentName
        self.logger.debug("Folder    = % s" % folderName)
        self.logger.debug("File      = % s" % documentPath)
        self.logger.debug("EndFile   = % s" % endDocumentPath)
        self.logger.debug("Ext.      = % s" % extension)
        if not os.path.isdir(fullDirPath):
            self.logger.debug("Creating directory '%s'"%fullDirPath)
            os.mkdir(fullDirPath)
        shutil.copy(documentPath, endDocumentPath)
        document = Document(fullDirPath)
        document.update(data, force = True)
        document.save()
