#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# abramsci/SAO/kit/saomat.py
"""
Seismicity Analysis Organizer - Metadata Audit Tool (SAOMAT)

Graphical User Interface for managing temporary networks metadata.
Based on ObsPy + DearPyGUI frameworks to leverage modern capabilities.

**Copyright:** 2023, Sergei Abramenkov (https://github.com/abramsci)

**License:** [GNU LGPL](../LICENSE)

**Dependencies:**
    * Python 3.11+ (because of `tomllib` and other nice things)
    * dearpygui (tested for 1.10.1)
    * icecream (tested for 2.1.3)
    * obspy (tested for 1.4.0)
    * pyyaml (tested for 6.0.1)
"""
################################### IMPORTS ###################################
# Python standard library imports
import tomllib
from pathlib import Path

# Necessary packages (not in standard lib)
import dearpygui.dearpygui as dpg
import yaml
from icecream import ic
from obspy import read_inventory, UTCDateTime
from obspy.core.inventory import Inventory, Network, Station, Channel



################################ APP CONSTANTS ################################
APP_TITLE : str = 'Seismicity Analysis Organizer - Metadata Audit Tool'
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR.joinpath('assets')
ICON_FILE = ASSETS_DIR.joinpath('SAO.ico')
DEFAULT_CONFIG_FILE = APP_DIR.joinpath('config.toml')
USER_DIR = Path.home().joinpath('.SAO')
USER_CONFIG_FILE = USER_DIR.joinpath('config.yaml')



############################## GLOBAL VARIABLES ###############################
workdir                 : Path = Path.home()
equipments              : dict[str: Station] = {}
inventories             : dict[str: Inventory] = {}
active_inventory_tag    : str = None
networks                : dict[str: Network] = {}
active_network_tag      : str = None
stations                : dict[str: Station] = {}
active_station_tag      : str   = None
# Defaults
lat_0 : float =  48.844931
lon_0 : float =   2.356216
ele_0 : float =  30.5



############################### SUPPORT CLASSES ###############################
class AppConfig:
    """Simple class to load / save app configuration attributes
    """
    def __init__(self, config_dict: dict):
        for key, value in config_dict.items():
            setattr(self, key, value)

    @classmethod
    def load_toml(cls, path: Path):
        with open(path, 'rb') as file:
            return cls(tomllib.load(file))

    @classmethod
    def load_yaml(cls, path: Path):
        with open(path, 'r') as file:
            return cls(yaml.safe_load(file))

    def __repr__(self):
        rows = [f'\t{key}: {value}' for key, value in self.__dict__.items()] 
        return 'Configured as follow:\n' + '\n'.join(rows)

    def save_yaml(self, path: Path):
        with open(path, 'w') as file:
            result = yaml.dump(self.__dict__, file)


class Panel:
    """Base class for interface panels - child windows in DearPyGUI.
    """
    def __init__(self, parent, tag, w, h, **kwargs):
        dpg.add_child_window(parent=parent, tag=tag, width=w, height=h, 
                             **kwargs)



############################## UTILITY FUNCTIONS ##############################
def add_dialog(tag, call, exts=None, **kwargs):
    """Arguably useful wrapping extention of premade DPG file dialog.
    """
    wv = dpg.get_viewport_width();  hv = dpg.get_viewport_height() 
    with dpg.file_dialog(tag=tag, callback=lambda s, a, u : call(s, a, u), 
                         min_size=[wv//2,hv//3], max_size=[wv//2,hv//2],
                         show=False, modal=True, **kwargs):
        if exts:
            for ext in exts:
                dpg.add_file_extension(ext)
        dpg.add_file_extension('.*')



################################## CALLBACKS ##################################
def edit_param_str(sender, app_data, user_data):
    """Basic attribute assignment for editing string fields. 

    Works assuming following naming scheme for DPG items:
        user_data   - has attribute named xxxxx
        sender      - DPG string alias ending with .xxxxx
        app_data    - whatever type acceptable for the attribute
    Example 1:
        user_data=inv           - obspy.Inventory instance
        sender='C.test.sender'  - text input for the inventory field `sender`
        app_data='IPGG SB RAS'  - string to be set for this attribute
    Example 2:
    """
    setattr(user_data, sender.split('.')[-1], app_data)


def edit_param_utc(sender, app_data, user_data):
    """Basic UTCDateTime field assignment from ISO string. 
    """
    setattr(user_data, sender.split('.')[-1], UTCDateTime(app_data))


def edit_param_code(sender, app_data, user_data, size: int=5):
    code = app_data[:size]
    setattr(user_data, sender.split('.')[-1], code)
    if sender.split('.')[-2] == 'station' and sender.split('.')[-1] == 'code':
        dpg.configure_item(active_station_tag, label=code)
    if sender.split('.')[-2] == 'network' and sender.split('.')[-1] == 'code':
        dpg.configure_item(active_network_tag, label=code)
    dpg.set_value(sender, code)


def create_station():
    global active_station_tag
    if not active_network_tag:
        print('Select network in the explorer window to add station to.')
        return
    net = networks[active_network_tag]
    net.stations.append(Station('XXXXX', lat_0, lon_0, ele_0,
                                start_date=net.start_date,
                                end_date=net.end_date,
                                restricted_status=net.restricted_status))
    add_station(net.stations[-1])
    active_station_tag = dpg.last_item()
    #dpg.set_value(active_station_tag, True)
    link_station(active_station_tag, True, net.stations[-1])


def create_network():
    if not active_inventory_tag:
        print('Select inventory in the explorer window to add network to.')
        return
    inv = inventories[active_inventory_tag]
    inv.networks.append(Network('XX', restricted_status='closed',
                                description='Temporary seismic network'))
    add_network(inv.networks[-1])


def create_inventory(sender, app_data, user_data):
    global workdir
    workdir = Path(app_data['current_path'])
    path = Path(app_data['file_path_name'])
    if path.exists():
        print('File already exists! Specify NEW file name, please.')
        return
    inv = Inventory(source='SAOMAT',
                    module=__doc__.split('\n')[1],
                    module_uri='https://github.com/abramsci/SAO',
                    created=UTCDateTime.now())
    inv.networks = []
    add_inventory(path.stem, inv)


def load_inventory(sender, app_data, user_data):
    global workdir
    workdir = Path(app_data['current_path'])
    inv = None
    path = Path(app_data['file_path_name'])
    try:
        inv = read_inventory(path)
    except TypeError:
        print('Not a Station-XML file!')
    add_inventory(path.stem, inv)


def save_changes():
    if not active_inventory_tag:
        print('Select inventory to save in the explorer window.')
        return
    inv = inventories[active_inventory_tag]
    # Making arrangements - mostly dublicating info from station to channels 
    for network in inv.networks:
        for station in network.stations:
            for channel in station.channels:
                for attr in ['latitude', 'longitude', 'elevation',
                             'start_date', 'end_date', 'restricted_status']:
                    if hasattr(station, attr):
                        setattr(channel, attr, getattr(station, attr))
                #print(channel)
            #print(station)
            if station.start_date:
                date = station.start_date
                #ic(date)
                for equipment in station.equipments:
                    equipment.installation_date = date
                for channel in station.channels:
                    if channel.sensor:
                        channel.sensor.installation_date = date
                    if channel.data_logger:
                        channel.data_logger.installation_date = date
                    if channel.pre_amplifier:
                        channel.pre_amplifier.installation_date = date
            if station.end_date:
                date = station.end_date
                #ic(date)
                for equipment in station.equipments:
                    equipment.removal_date = date
                for channel in station.channels:
                    if channel.sensor:
                        channel.sensor.removal_date = date
                    if channel.data_logger:
                        channel.data_logger.removal_date = date
                    if channel.pre_amplifier:
                        channel.pre_amplifier.removal_date = date
            if station.historical_code:
                logger_code = station.historical_code
                ic(logger_code)
                for channel in station.channels:
                    if channel.data_logger:
                        channel.data_logger.serial_number = logger_code

    path = workdir.joinpath(f'{active_inventory_tag}.xml')
    # Back-up existing path just in case
    if path.exists():
        time = UTCDateTime.now().format_fissures().split('.')[0]
        bckp = USER_DIR.joinpath(f'{time}.{active_inventory_tag}.xml')
        with open(path, 'r') as s, open(bckp, 'w') as t:
            t.write(s.read())
    print(f'Saving to {path}')
    print(inv)
    inv.write(path, 'STATIONXML')
    print('Done.')    


def load_equipment(sender, app_data, user_data):
    global workdir
    workdir = Path(app_data['current_path'])
    inv = None
    path = Path(app_data['file_path_name'])
    try:
        inv = read_inventory(path)
    except TypeError:
        print('Not a Station-XML file!')
    print(inv)
    add_equipment(path.stem, inv.networks[-1].stations[-1])
    

def link_station(sender, app_data, user_data):
    global active_station_tag
    if not app_data:
        active_station_tag = None
        dpg.configure_item('C.station', show=False)
        dpg.configure_item('D.station', show=False)
        return
    active_station_tag = sender
    sta = stations[active_station_tag]
    for choice in user_data:
        if choice != sender:
            dpg.set_value(choice, False)
    # Linking context panel content to the chosen station  
    dpg.configure_item('C.station.code', user_data=sta,
                       default_value=sta.code,
                       callback=lambda s, a, u:
                       edit_param_code(s, a, u, size=5))
    dpg.configure_item('C.station.historical_code', user_data=sta,
                       default_value=sta.historical_code,
                       callback=lambda s, a, u:
                       edit_param_code(s, a, u, size=5))
    dpg.configure_item('C.station.restricted_status', user_data=sta,
                       default_value=sta.restricted_status,
                       callback=lambda s, a, u:
                       edit_param_str(s, a, u))
    # dpg.configure_item('C.station.alternate_code', user_data=sta,
    #                    default_value=sta.alternate_code,
    #                    callback=lambda s, a, u:
    #                    edit_param_code(s, a, u, size=5))
    dpg.configure_item('C.station.latitude', user_data=sta,
                       default_value=sta.latitude,
                       callback=lambda s, a, u:
                       edit_param_str(s, a, u))
    dpg.configure_item('C.station.longitude', user_data=sta,
                       default_value=sta.longitude,
                       callback=lambda s, a, u:
                       edit_param_str(s, a, u))
    dpg.configure_item('C.station.elevation', user_data=sta,
                       default_value=sta.elevation,
                       callback=lambda s, a, u:
                       edit_param_str(s, a, u))
    dpg.configure_item('D.station.start_date', user_data=sta,
                       default_value=sta.start_date,
                       callback=lambda s, a, u:
                       edit_param_utc(s, a, u))
    dpg.configure_item('D.station.end_date', user_data=sta,
                       default_value=sta.end_date,
                       callback=lambda s, a, u:
                       edit_param_utc(s, a, u))
    dpg.configure_item('C.station', show=True)
    dpg.configure_item('D.station', show=True)


def link_network(sender, app_data, user_data):
    global active_network_tag, active_station_tag
    if not app_data:
        if active_station_tag:
            dpg.set_value(active_station_tag, False)
        active_station_tag = None
        dpg.configure_item('C.station', show=False)
        dpg.configure_item('D.station', show=False)
        active_network_tag = None
        dpg.configure_item('C.network', show=False)
        dpg.configure_item('D.network', show=False)
        return
    active_network_tag = sender
    net = networks[active_network_tag]
    for choice in user_data:
        if choice != sender:
            dpg.set_value(choice, False)
        else:
            dpg.configure_item('C.network.code', user_data=net,
                               default_value=net.code,
                               callback=lambda s, a, u:
                               edit_param_code(s, a, u, size=2))
            dpg.configure_item('C.network.restricted_status', user_data=net,
                               default_value=net.restricted_status,
                               callback=lambda s, a, u:
                               edit_param_str(s, a, u))
            dpg.configure_item('D.network.start_date', user_data=net,
                               default_value=net.start_date,
                               callback=lambda s, a, u:
                               edit_param_utc(s, a, u))
            dpg.configure_item('D.network.end_date', user_data=net,
                               default_value=net.end_date,
                               callback=lambda s, a, u:
                               edit_param_utc(s, a, u))
            dpg.configure_item('C.network', show=True)
            dpg.configure_item('D.network', show=True)


def link_inventory(sender, app_data, user_data):
    global active_inventory_tag, active_network_tag, active_station_tag
    if not app_data:
        if active_station_tag:
            dpg.set_value(active_station_tag, False)
        active_station_tag = None
        dpg.configure_item('C.station', show=False)
        dpg.configure_item('D.station', show=False)
        if active_network_tag:
            dpg.set_value(active_network_tag, False)
        active_network_tag = None
        dpg.configure_item('C.network', show=False)
        dpg.configure_item('D.network', show=False)
        active_inventory_tag = None
        dpg.configure_item('C.inventory', show=False)
        return
    active_inventory_tag = sender
    inv = inventories[active_inventory_tag]
    for choice in user_data:
        if choice != sender:
            dpg.set_value(choice, False)
        else:
            dpg.set_value('C.inventory.name',
                          f'Inventory\n|{active_inventory_tag}|')
            dpg.configure_item('C.inventory.source', user_data=inv,
                               default_value=inv.source,
                               callback=lambda s, a, u:
                               edit_param_str(s, a, u))
            dpg.configure_item('C.inventory.sender', user_data=inv,
                               default_value=inv.sender,
                               callback=lambda s, a, u:
                               edit_param_str(s, a, u))
            dpg.configure_item('C.inventory.created', user_data=inv,
                               default_value=inv.created,
                               callback=lambda s, a, u:
                               edit_param_utc(s, a, u))
            dpg.configure_item('C.inventory', show=True)


def equip(sender, app_data, user_data):
    stations[sender].channels = app_data.channels
    stations[sender].equipments = app_data.equipments



def add_station(sta):
    stations[dpg.add_selectable(parent='stations', label=sta.code)] = sta
    # Reconfiguring all respective selectables to know about new one
    for selectable in stations.keys():
        dpg.configure_item(selectable, user_data=stations,
                           callback=lambda s, a, u: link_station(s, a, u),
                           payload_type='station',
                           drop_callback=lambda s, a, u: equip(s, a, u))


def add_network(net):
    networks[dpg.add_selectable(parent='networks', label=net.code)] = net
    # Reconfiguring all respective selectables to know about new one
    for selectable in networks.keys():
        dpg.configure_item(selectable, user_data=networks,
                           callback=lambda s, a, u: link_network(s, a, u))


def add_inventory(name, inv):
    if not inv.source or name in inventories:
        return
    # Adding inventory to dictionary with its dpg.selecatable tag key
    with dpg.group(parent='inventories', indent=pad):
        inventories[dpg.add_selectable(tag=name, label=name)] = inv
        # Forming visual tree of inventory content
        for net in inv.networks:
            add_network(net)
            with dpg.tree_node(label=net.code, bullet=True,
                               open_on_double_click=True):
                for sta in net.stations:
                    add_station(sta)
                    with dpg.tree_node(label=sta.code, bullet=True,
                                       open_on_double_click=True):
                        for cha in sta.channels:
                            dpg.add_text(cha.code, bullet=True)
    # Reconfiguring all selectables - inventories keys to know about new one
    for selectable in inventories.keys():
        dpg.configure_item(selectable, user_data=inventories,
                           callback=lambda s, a, u: link_inventory(s, a, u))


def add_equipment(name, station):
    if not station or name in equipments:
        return
    equipments[dpg.add_button(parent='equipments', label=name)] = station
    with dpg.drag_payload(parent=dpg.last_item(), drag_data=station,
                          payload_type='station'):
        dpg.add_text('\n'.join([str(equip) for equip in station.equipments]))



################################# APPLICATION #################################
class MetadataAuditTool:    
    """Base class for managing app style, resizing and other system calls.
    """ 
    width   : int = None
    height  : int = None


    def __init__(self):
        """Should be called after DPG context but before viewport creation.
        """
        with dpg.window(tag='app-window'):
            with dpg.menu_bar(tag='main-menu'):
                with dpg.menu(label="Tools"):
                    dpg.add_menu_item(label='Show Style Editor',
                                      callback=lambda:
                                      dpg.show_tool(dpg.mvTool_Style))
                    dpg.add_menu_item(label='Show Item Registry', 
                                      callback=lambda:
                                      dpg.show_tool(dpg.mvTool_ItemRegistry))
                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Toggle Fullscreen",
                                      callback=lambda:
                                      dpg.toggle_viewport_fullscreen())
        dpg.set_primary_window('app-window', True)


    def set_look_and_feel(self, config: AppConfig):
        """Setting unique look and feel tweaking DearPyGUI defaults.
        IMPORTANT: dpg.create_context() must be called before this function!
        """
        if hasattr(config, 'font'):
            with dpg.font_registry():
                for goal, font in config.font.items():
                    with dpg.font(ASSETS_DIR.joinpath(font['file']),
                                font['size'], tag=f'font-{goal}'):
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            if 'base' in config.font:
                dpg.bind_font(f'font-base')
        if hasattr(config, 'theme'):
            cfg = AppConfig(config.theme)
            ic(cfg)
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvAll):
                    if hasattr(cfg, 'style'):
                        for key, value in cfg.style.items():
                            var = getattr(dpg, f'mvStyleVar_{key}')
                            if type(value) == list:
                                dpg.add_theme_style(var, value[0], value[1])
                            else:
                                dpg.add_theme_style(var, value)
                    if hasattr(cfg, 'color'):
                        for key, values in cfg.color.items():
                            var = getattr(dpg, f'mvThemeCol_{key}')
                            dpg.add_theme_color(var, values)
            dpg.bind_theme(theme)


    def reset(self, layout: AppConfig):
        """7-PANELS LAYOUT REWISED
            X++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++X
            +=MAINMENU====================STATUSLINE/PROGRESSBAR=========+
            +/----------\/------\/----------------------\/--------------\+
            +|=LSUBMENU=||      ||                      ||=====RSUBMENU=|+
            +|          ||      ||                      ||              |+
            +| EXPLORER ||  C   ||        DATES         ||     KNOBS    |+
            +|    A     ||  O   ||          D           ||       B      |+
            +|          ||  N   ||                      |\--------------/+
            H|          ||  T   ||                      |/--------------\+
            V|          ||  E   |\----------------------/|              |+
            +\----------/|  X   |/----------------------\|              |+
            +/----------\|  T   ||                      ||              |+
            +|          ||      ||                      ||              |+
            +|  GRAPH   H|  C   H|        FOCUS         H|     NOTES    H+
            +|    G     L|      W|          F           F|       E      R+
            +|          ||      ||                      ||              |+
            +\------WL--/\--WW--/\------------------WF--/\----------WR--/+
            X++++++++++++++++++++++++++++++WV++++++++++++++++++++++++++++X
        """
        # Getting respective sizes of layout elements
        global pad, wwrd, wcol, hrow
        pad = layout.pad;       wwrd = layout.wwrd
        wcol = layout.wcol;     hrow = layout.hrow
        wl = layout.wl;         hl = layout.hl
        wr = layout.wr;         hr = layout.hr
        wa = layout.wl;         ha = layout.hc - layout.hl - layout.pad
        wb = layout.wr;         hb = layout.hc - layout.hr - layout.pad
        wc = layout.wc;         hc = layout.hc
        wd = layout.wf;         hd = layout.hc - layout.hf - layout.pad
        we = layout.wr;         he = layout.hr
        wf = layout.wf;         hf = layout.hf
        wg = layout.wl;         hg = layout.hl
        self.width  = 7 * pad + wl + wc + wf + wr
        self.height = hc + 3 * pad + hrow
        
        # Setting up GUI layout core
        with dpg.group(parent='app-window', tag='layout', horizontal=True):
            with dpg.group(tag='left-dock'):
                self.explorer = Panel('left-dock', 'A', wa, ha, menubar=True)
                self.graph = Panel('left-dock', 'G', wg, hg)
            self.context = Panel('layout', 'C', wc, hc)
            with dpg.group(tag='center'):
                self.dates = Panel('center', 'D', wd, hd)
                self.focus = Panel('center', 'F', wf, hf)
            with dpg.group(tag='right-dock'):
                self.knobs = Panel('right-dock', 'B', wb, hb, menubar=True)
                self.notes = Panel('right-dock', 'E', we, he)
        # PANEL-A: explorer
        with dpg.menu_bar(parent='A', tag='A.menu'):
            with dpg.menu(label='Inventory        '):
                add_dialog('create-inventory', create_inventory,
                           exts=['Station-XML {.xml}'], default_path=workdir,
                           label='Type new inventory name')
                dpg.add_menu_item(label='Create new',
                                  user_data='create-inventory',
                                  callback=lambda s, a, u:
                                  dpg.configure_item(u, show=True))
                add_dialog('load-inventory', load_inventory,
                           exts=['Station-XML {.xml}'], default_path=workdir,
                           label='Load Station-XML')
                dpg.add_menu_item(label='Load Station-XML',
                                  user_data='load-inventory',
                                  callback=lambda s, a, u:
                                  dpg.configure_item(u, show=True))
                dpg.add_menu_item(label='Save changes', callback=save_changes)
            with dpg.menu(label='Network'):
                dpg.add_menu_item(label='Add new', callback=create_network)
            with dpg.menu(label='Station  '):
                dpg.add_menu_item(label='Add new', callback=create_station)
        with dpg.group(parent='A', tag='A.content', horizontal=True):
            dpg.add_child_window(tag='inventories', width=wcol+wwrd)
            dpg.add_child_window(tag='networks', width=wwrd+2*pad)
            dpg.add_child_window(tag='stations', width=wcol-2*pad)
        # PANEL-B: knobs
        with dpg.menu_bar(parent='B', tag='B.menu'):
            with dpg.menu(label='Equipment'):
                add_dialog('load-equipment', load_equipment,
                           exts=['Station-XML {.xml}'], default_path=workdir,
                           label='Load a file with equipment response')
                dpg.add_menu_item(label='Load Station-XML',
                                  user_data='load-equipment',
                                  callback=lambda s, a, u:
                                  dpg.configure_item(u, show=True))
        dpg.add_group(parent='B', tag='equipments')
        # PANEL-C: context        
        with dpg.group(parent='C', tag='C.inventory', show=False):
            dpg.add_text('Inventory\n||', tag='C.inventory.name')
            dpg.add_input_text(tag='C.inventory.source', label='source',
                               width=wcol, on_enter=True)
            dpg.add_input_text(tag='C.inventory.sender', label='sender',
                               width=wcol, on_enter=True)
            dpg.add_input_text(tag='C.inventory.created', label='created',
                               width=2*wcol, on_enter=True)
        dpg.add_separator(parent='C')
        with dpg.group(parent='C', tag='C.network', show=False):
            dpg.add_input_text(tag='C.network.code', label='network code',
                               width=wwrd, on_enter=True, uppercase=True,
                               no_spaces=True, hint='XX')
            dpg.add_combo(tag='C.network.restricted_status',
                          items=('open', 'closed', 'partial'))
        dpg.add_separator(parent='C')
        with dpg.group(parent='C', tag='C.station', show=False):
            dpg.add_input_text(tag='C.station.code', label='station code',
                               width=wwrd, on_enter=True, uppercase=True,
                               no_spaces=True, hint='XXXXX')
            dpg.add_input_text(tag='C.station.historical_code',
                               label='historical', width=wwrd, on_enter=True,
                               uppercase=True, no_spaces=True, hint='STA09')
            dpg.add_combo(tag='C.station.restricted_status',
                          items=('open', 'closed', 'partial'))
            # dpg.add_input_text(tag='C.station.alternate_code',
            #                    label='alternate', width=wwrd, on_enter=True,
            #                    uppercase=True, no_spaces=True, hint='ABC09')
            dpg.add_spacer()
            # TODO: think about workaround for nested attributes...
            # dpg.add_input_text(tag='site.name', label='site',
            #                    width=wcol, on_enter=True)
            dpg.add_input_double(tag='C.station.latitude', label='° N/S',
                                 width=wcol, on_enter=True,
                                 min_value=-90.0, max_value=90.0,
                                 min_clamped=True, max_clamped=True,
                                 format='%11.6f', step=0)
            dpg.add_input_double(tag='C.station.longitude', label='° E/W',
                                 width=wcol, on_enter=True,
                                 min_value=-180.0, max_value=180.0,
                                 min_clamped=True, max_clamped=True,
                                 format='%11.6f', step=0)
            dpg.add_input_float(tag='C.station.elevation', label='m Z',
                                width=2*wcol//3, on_enter=True,
                                format='%7.1f', step=0, indent=wcol//3)
        # PANEL-D: dates
        with dpg.group(parent='D', tag='D.network', show=False):
            dpg.add_input_text(tag='D.network.start_date',
                               label='Network start date',
                               width=2*wcol, on_enter=True)
            dpg.add_input_text(tag='D.network.end_date',
                               label='Network end date (None if active)',
                               width=2*wcol, on_enter=True)
        dpg.add_separator(parent='D')
        with dpg.group(parent='D', tag='D.station', show=False):
            dpg.add_input_text(tag='D.station.start_date',
                               label='Station start date',
                               width=2*wcol, on_enter=True)
            dpg.add_input_text(tag='D.station.end_date',
                               label='Station end date (None if active)',
                               width=2*wcol, on_enter=True)
        # After reset - return new widht and height to adjust viewport
        return self.width, self.height



############################## GUI APP LIFECYCLE ##############################
if __name__ == '__main__':
    #print('\n'.join(__doc__.split('\n')[1:8]), '\nLoading configuration...')
    if USER_CONFIG_FILE.is_file():
        config_path = USER_CONFIG_FILE
        #print(f'Using user configuration: {config_path}')
        cfg = AppConfig.load_yaml(config_path)
        workdir = Path(cfg.workdir)
    else:
        config_path = DEFAULT_CONFIG_FILE
        #print(f'Using default app configuration: {config_path}')
        cfg = AppConfig.load_toml(config_path)
    dpg.create_context()            # Figuring out OS and hardware capabilities
    app = MetadataAuditTool()       # Instancing primary window
    app.set_look_and_feel(cfg)      # Setting up styles and fonts
    dpg.create_viewport(title=APP_TITLE, large_icon=str(ICON_FILE))
    width, height = app.reset(AppConfig(cfg.layout))    # Setting up layout
    dpg.set_viewport_width(width);  dpg.set_viewport_height(height)
    dpg.setup_dearpygui()           # Preparing
    dpg.show_viewport()             # Presenting
    dpg.start_dearpygui()           # Launching
    # Saving working directory for next launch 
    cfg.workdir = str(workdir)
    USER_DIR.mkdir(exist_ok=True)
    cfg.save_yaml(USER_CONFIG_FILE)
    dpg.destroy_context()           # Cleaning up
    # Return error code 0 back to shell if everything works ok.
    exit(0)
###############################################################################