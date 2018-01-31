import os
import re
import json
from tkinter import *
from tkinter.ttk import *
from utils import mingle
from utils import release

base_dir = r'/home/cwilkins/'

class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        s = Style()
        print(s.theme_names())
        s.theme_use('alt')
        self.pack(fill=BOTH, expand=1)
        self.current_system_widgets = []
        self.create_widgets()
        self.save_button = None
        self.set_button = None
        self.mingle_number = None
        self.release = None

    def create_widgets(self):
        self.note = Notebook(self)
        self.tab1 = Frame(self.note)
        self.tab2 = Frame(self.note)
        p = Panedwindow(self.tab1, orient=VERTICAL)
        f1 = Labelframe(p, text='Create Mingle', width=200, height=100)
        f2 = Labelframe(p, text='Use Mingle', width=100, height=100)
        p.add(f1)
        p.add(f2)
        self.start_option = '<Select a Deployment>'
        self.deployment_option = '<Select a System>'
        mingle_list = [self.start_option]
        system_list = [self.deployment_option, 'sim1-system-1-A']

        deployment_list = mingle.get_active_deployments()
        for deployment in deployment_list:
            mingle_list.append('MINGLE-{} - {}'.format(deployment.number,
                                                       deployment.name.encode('utf-8').decode('utf-8')))

        self.variable = StringVar(self.tab1)
        self.variable.set(mingle_list[0])
        OptionMenu(f2, self.variable, *mingle_list, command=self.on_deploy_select).pack()
        self.env_var = StringVar(self.tab2)
        self.env_var.set(system_list[0])
        OptionMenu(self.tab2, self.env_var, *system_list, command=self.on_system_select).grid(row=0, columnspan=3)
        p.pack()
        self.note.add(self.tab1, text="First tab")
        self.note.add(self.tab2, text="Second tab")
        self.note.pack(fill=BOTH, expand=1)
        self.note.select(self.tab1)
        self.note.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        Button(self.tab1, text='Next', command=self.on_change_tab).pack()

    def on_deploy_select(self, event):
        selected_deployment = self.variable.get()
        if 'MINGLE-' in selected_deployment:
            matches = re.search('MINGLE-(\d+)', selected_deployment)
            self.mingle_number = matches.group(1)

    def on_tab_changed(self, event):
        selected_tab = event.widget.index("current")
        if selected_tab == 1:
            print('Changed tab to {}'.format(selected_tab))
            if not self.release:
                self.release = release.Release(self.mingle_number)

    def on_change_tab(self):
        if self.variable.get() == self.start_option:
            print('Select a deployment')
        else:
            self.note.select(self.tab2)

    def on_system_select(self, event):
        selected_system = self.env_var.get()
        if selected_system != self.deployment_option:
            self.clear_frame()
            system_type = selected_system.split('-')[0]
            sub_dir = os.path.join(base_dir, system_type)
            self.target_json = os.path.join(sub_dir, '{}-sys.json'.format(selected_system))
            if os.path.isfile(self.target_json):
                system_json = json.load(open(self.target_json, 'r'))

                def handler(event, self=self):
                    return self.on_spin_update(event)

                for i in range(len(system_json['apps'])):
                    lb = Label(self.tab2, text=system_json['apps'][i]['service'])
                    lb.grid(row=i + 1)
                    sb = Spinbox(self.tab2, name="box_{}".format(i), from_=1, to_=100)
                    sb.delete(0, END)
                    sb.insert(0, system_json['apps'][i]['version'])
                    sb.grid(row=i + 1, column=2)

                    sb.bind('<Button-1>', handler)
                    self.current_system_widgets.append((lb, sb))

                # now config and tools
                config_lb = Label(self.tab2, text="config")
                config_lb.grid(row=len(system_json['apps']) + 1)
                config_sb = Spinbox(self.tab2, from_=1, to_=100)
                config_sb.delete(0, END)
                config_sb.insert(0, system_json['config']['version'])
                config_sb.grid(row=len(system_json['apps']) + 1, column=2)
                config_sb.bind('<Button-1>', handler)
                self.tab2.rowconfigure(len(system_json['apps']) + 1, pad=25)

                tools_lb = Label(self.tab2, text="tools")
                tools_lb.grid(row=len(system_json['apps']) + 2)
                tools_sb = Spinbox(self.tab2, from_=1, to_=100)
                tools_sb.delete(0, END)
                tools_sb.insert(0, system_json['tools_version'])
                tools_sb.grid(row=len(system_json['apps']) + 2, column=2)
                tools_sb.bind('<Button-1>', handler)

                self.current_system_widgets.append((config_lb, config_sb))
                self.current_system_widgets.append((tools_lb, tools_sb))
                self.set_all = Spinbox(self.tab2, from_=1, to_=100)
                self.set_all.bind('<Button-1>', handler)
                self.set_all.grid(row=len(system_json['apps']) + 3, column=0)
                self.set_button = Button(self.tab2, text='Set All', command=self.update_all)
                self.set_button.grid(row=len(system_json['apps']) + 3, column=1)
                self.save_button = Button(self.tab2, text='Save', command=self.save_changes)
                self.save_button.grid(row=len(system_json['apps']) + 3, column=2)
        else:
            self.clear_frame()

    def on_spin_update(self, event):
        current_value = event.widget.get()
        if '-SNAPSHOT' in current_value:
            return

        if '.' in current_value:
            current_major = current_value.split('.')[0]
            current_decimal = int(current_value.split('.')[-1])
            target_decimal = current_decimal + 1
            if len(str(current_decimal)) != len(str(target_decimal)):
                target_value = '{}.0{}'.format(current_major, current_decimal)
                event.widget.delete(0, END)
                event.widget.insert(0, target_value)
            event.widget.config(increment=float(1)/float(10 ** int(len(str(target_decimal)))))

    def update_all(self):
        target_value = self.set_all.get()
        for widget in self.current_system_widgets:
            widget[1].delete(0, END)
            widget[1].insert(0, target_value)

    def save_changes(self):
        if self.release:
            print('Saving')
            app_json = []
            for widget in self.current_system_widgets:
                print(widget[0].winfo_class(), widget[1].winfo_class())
                component_name = widget[0].cget('text')
                component_version =  widget[1].get()
                if component_name == 'config':
                    self.release.update_config_version(self.target_json, component_version)
                elif component_name == 'tools':
                    self.release.update_tools_version(self.target_json, component_version)
                else:
                    app_json.append({'service': component_name, 'version': component_version})

            self.release.update_apps(self.target_json, app_json)
            
    def clear_frame(self):
        grid_dimensions = self.tab2.grid_size()
        for row in range(grid_dimensions[1]):
            self.tab2.rowconfigure(row, pad=0)

        for widget in self.current_system_widgets:
            widget[0].destroy()
            widget[1].destroy()

        if self.save_button:
            self.save_button.destroy()

        if self.set_button:
            self.set_button.destroy()
            self.set_all.destroy()

        self.current_system_widgets = []


class ORMFrame():
    def __init__(self):
        root = Tk()
        #root['bg'] = 'white'
        app = Application(master=root)
        app.mainloop()
