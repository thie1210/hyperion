import re
import sublime, sublime_plugin  
  
class BookmarkEmptyCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        view = self.view
        sels = self.view.sel()
        view.run_command('clear_bookmarks')
        regions = view.find_all('(?<=msgstr ")(?="\n\n)')
        for region in regions:
            sels.clear()
            sels.add(region)
            self.view.run_command('toggle_bookmark')
            
class BookmarkFuzzyCommand(sublime_plugin.TextCommand):  
    def run(self, edit):
        view = self.view
        sels = self.view.sel()
        view.run_command('clear_bookmarks')
        regions = view.find_all('#, fuzzy')
        for region in regions:
            single_line = view.find('msgstr ".*"', region.a)
            multi_line = view.find('msgstr ""\n"', region.a)
            if single_line is None:
                msgstr_region = view.find('(?<=msgstr ""\n")', region.a)
            elif multi_line is None:
                msgstr_region = view.find('(?<=msgstr ")', region.a)
            elif single_line.a < multi_line.a:
                msgstr_region = view.find('(?<=msgstr ")', region.a)
            else:
                msgstr_region = view.find('(?<=msgstr ""\n")', region.a)
            sels.clear()
            sels.add(msgstr_region)
            self.view.run_command('toggle_bookmark')

class ToggleFuzzyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sels = view.sel()
        msgid_line = None
        last_line = view.find('(?<=\n\n)', sels[0].a)
        current_line = view.line(last_line)
        while msgid_line == None:
            current_string = view.substr(current_line)
            if re.match('^\n$', current_string):
                return
            match = re.match('^msgid', current_string)
            if match:
                msgid_line = current_line
            else:
                current_line = view.line(current_line.a - 1)
        prev_line = view.line(msgid_line.a - 1)
        prev_string = view.substr(prev_line)
        if re.match('^#:', prev_string):
            view.insert(edit, msgid_line.a, '#, fuzzy\n')
        elif re.match ('^#, fuzzy, .*-format', prev_string):
            erase_region = view.find('fuzzy, ', prev_line.a)
            view.erase(edit, erase_region)
        elif re.match('^#, .*-format', prev_string):
            view.insert(edit, prev_line.a + 3, 'fuzzy, ')
        elif re.match('^#, fuzzy$', prev_string):
            view.erase(edit, view.full_line(prev_line))
        else:
            pass
        # view.run_command('next_bookmark')
# FindPrevEmpty
# FindNextFuzzy
# FindPrevFuzzy
# ToggleFuzzy