#!/usr/bin/env python
# *-* coding: utf8 *-*

import os, subprocess

from distutils.core import setup
from distutils.cmd import Command
from distutils.filelist import findall
from glob import glob


class BuildDoc(Command):
    description = "Generate projet documentation using pydoc"
    user_options = []
    doc_src="src"
    doc_dst="doc/api"
    exceptions=['__init__.py']
  
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pydoc, sys

        def walk(base, prefix, element):
            """Recursively walk through the base directory. 
            Return a list of python modules in this directory."""
            path = os.path.join(base, element)
            if os.path.isdir(path):
                if os.path.isfile(os.path.join(path, '__init__.py')):
                    l = [element]
                    if len(prefix) == 0:
                        subprefix = element
                    else:
                        subprefix = '.'.join([prefix, element])
                else:
                    l = []
                    subprefix = ''
                for subpath in os.listdir(path):
                    l += walk(path, subprefix, subpath)
                return l
            elif element.endswith('.py') and not element == '__init__.py':
                return ['.'.join([prefix, os.path.splitext(element)[0]])]
            else:
                return []

        sys.path.insert(0, Doc.doc_src)
        file_list = walk(Doc.doc_src, '', '')
        for f in file_list:
            pydoc.writedoc(f)
            doc_file = f+'.html'
            os.rename(doc_file, os.path.join(Doc.doc_dst, doc_file))
   
class InstallDoc(Command):
    description = "install projet documentation"
    user_options = [('install-dir=', 'd', "directory to install doc files to")]
    
    docs = [('api', glob('doc/api/*')),
            ('manual', glob('doc/manual/_build/html/*/*')),
            ('examples', glob('doc/examples/*'))]
    
    def initialize_options(self) :
        self.install_dir = None
    def finalize_options(self) :
        pass

    def get_outputs(self) :
        return self.outputs

    def run(self) :
        self.outputs = []
        for (destination, files) in docs:
            d = os.path.join(self.install_dir, destination)
            self.mkpath(os.path.dirname(d))
            for f in files:
                elf.copy_file(f, d)
            self.outputs.append(d)

class BuildCatalog(Command):
    description = "build translation catalog from source files"
    user_options = []

    def initialize_options(self) :
        pass
        
    def finalize_options(self) :
        pass
        
    def run(self) :
        self.outputs = []
        PO_DIR = 'po'
        #extract messages from source files,
        src = glob('src/emulica/emulicapp/*.py') + glob('src/emulica/*.py') + ['src/emulica.py', 'ui/emulica.ui']
        #print "source files: ", src
        pot = os.path.join(PO_DIR, 'emulica.pot')
        common_opt = ['--keyword=_', '--keyword=N_', '--output=%s' % pot]
        #print ['/usr/bin/xgettext', '--language=python'] + common_opt + src[:-1]
        subprocess.call(['/usr/bin/xgettext', '--language=python'] + common_opt + src[:-1])
        #print ['xgettext', '--join-existing', '--language=glade'] + common_opt + [src[-1]]
        subprocess.call(['xgettext', '--join-existing', '--language=glade'] + common_opt + [src[-1]])
        print "updating messages catalog %s" % pot
        poFiles = filter(os.path.isfile, glob(os.path.join(PO_DIR,'*.po')))
        for pofile in poFiles:
            #fuzzyfy .po based on the new .pot catalog
            print "merging new messages in %s" % pofile
            subprocess.call(['msgmerge', '-U', pofile, pot])


class BuildLocales(Command):
    description = "build translation files"
    user_options = []

    def initialize_options(self) :
        pass
    def finalize_options(self) :
        pass

    def run(self) :
        for po in glob("po/*.po") :
            mo = po[:-2]+'mo'
            subprocess.call(['msgfmt', '-c', po, '-o', mo])
            print "building %s into %s" % (po, mo)


class InstallLocales(Command):
    description = "install translation files"
    user_options = [('install-dir=', 'd', "directory to install locale files to")]

    def initialize_options(self):
        self.install_dir = None
        
    def finalize_options(self):
        if self.install_dir is None:
            self.install_dir = 'dist/locales'
    
    def get_outputs(self):
        return self.outputs

    def run(self):
        self.run_command('build_locales')
        install_path = os.path.join(os.path.join(os.path.join(self.install_dir,"%s"),"LC_MESSAGES"),"emulica.mo")
        self.outputs = []
        for mo in glob("po/*.mo") :
            d = install_path % os.path.basename(mo)[:-3]
            self.mkpath(os.path.dirname(d))
            self.copy_file(mo, d)
            self.outputs.append(d)


class InstallIcons(Command):
    description = "install graphic files required by emulica"
    user_options = [('install-dir=', 'd', "directory to install icons files to")]
    
    def initialize_options(self):
        self.install_dir = None
        
    def finalize_options(self):
        if self.install_dir is None:
            self.install_dir = 'dist/icons'
    
    def get_outputs(self):
        return self.outputs

    def run(self):
        pass



data_files = [('icons', glob('ui/*.png')),
              ('.', ['ui/emulica.ui', 'ui/emulica-icon.png'])]

try:
    import py2exe
    class MyPy2Exe(py2exe.build_exe.py2exe):
        def run(self):
            import matplotlib as mpl
            for e in mpl.get_py2exe_datafiles():
                data_files.append(e)
            
            
            py2exe.build_exe.py2exe.run(self)
        
except ImportError:
    class MyPy2Exe():
        def run(self):
            print "py2exe not found"


setup(name='Emulica',
      version='0.6',
      description='Systemic Emulation Modeling and Execution Environment',
      author='Rémi Pannequin, Research Center for Automatic Control',
      author_email='remi.pannequin@cran.uhp-nancy.fr',
      license='GNU General Public License (GPL)',
      url='http://emulica.sourceforge.net/',
      packages=['emulica', 'emulica.emulicapp'],
      package_dir={'emulica': 'src/emulica'},
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Simulations '
          ],
      windows=[{'script': 'src/emulica.py',
                'icon_resources': [(1, 'ui/emulica-icon.ico')]}],
      options = {
        'py2exe': {
            'includes': ['cairo', 'pango', 'pangocairo', 'atk', 'gobject'],
            'excludes': ['_tkagg', 'tcl', 'pywin', 'pywin.debbuger', 'pywin.debugger.dbgcon', 'pywin.dialog', 'pywin.dialogs.list', 'Tkconstants', 'Tkinter'],
            'dll_excludes': 'libxml2-2.dll'}
            },
      scripts=['scripts/emulica'],
      data_files = data_files,
      cmdclass = {'install_locales': InstallLocales,
                  'build_locales': BuildLocales,
                  'catalog': BuildCatalog,
                  'doc': BuildDoc, 
                  'install_doc': InstallDoc,
                  'py2exe': MyPy2Exe}
     )


