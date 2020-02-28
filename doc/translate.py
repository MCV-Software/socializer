from babel.messages.frontend import CommandLineInterface

CommandLineInterface().run(['pybabel', 'extract', '-o', 'socializer-documentation.pot', '.'])
#CommandLineInterface().run(['pybabel','compile','-d','../src/locales'])
CommandLineInterface().run(['pybabel','update', '--input-file', 'socializer-documentation.pot', '--domain', 'socializer-documentation', '--output-dir', '../src/locales'])