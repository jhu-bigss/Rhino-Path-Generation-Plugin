################################################################################
# PathDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import rhinoscriptsyntax as rs
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

from RegistrationDialog import RegistrationDialog
from TopographyPath import TopographyPath

class PathDialog(forms.Dialog[bool]):

    def __init__(self):
        self.Title = 'Laser Path Generation'
        self.Paddomg = drawing.Padding(5)
        self.Resizable = False

        # *** Window Layout ***
        layout = forms.DynamicLayout(Padding = drawing.Padding(10, 5), DefaultSpacing = drawing.Size(2,2))

        # Status Textbox, non-edit
        status_label = forms.Label(Text = 'Status: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.status_textbox = forms.TextBox(Text = 'Get Started', TextAlignment = forms.TextAlignment.Center)
        self.status_textbox.ReadOnly = True
        
        layout.BeginVertical()
        layout.AddRow(status_label, self.status_textbox)
        layout.EndVertical()
        
        # = Begin of group boxes =
        layout.BeginVertical()
        # ---------------------------
        # - Registration group box -
        registration_groupbox = forms.GroupBox(Text = 'Implant', Padding = 5)
        
        self.register_button = forms.Button(Text = 'Registration')
        self.register_button.Click += self.OnRegisterButtonClick
        
        grouplayout = forms.DynamicLayout()
        grouplayout.AddRow(self.register_button)
        registration_groupbox.Content = grouplayout
        
        layout.AddRow(registration_groupbox)
        
        # ---------------------------
        # - Topography Path group box -
        topography_groupbox = forms.GroupBox(Text = 'Topography Path', Padding = 5)
        
        self.topo_config_btn = forms.Button(Text = 'Configure')
        self.topo_config_btn.Click += self.OnTopoConfigButtonClick
        
        self.topo_gen_btn = forms.Button(Text = 'Generate')
        self.topo_gen_btn.Click += self.OnTopoGenButtonClick
        
        grouplayout = forms.DynamicLayout()
        grouplayout.AddRow(self.topo_config_btn,'  ', self.topo_gen_btn)
        topography_groupbox.Content = grouplayout
        
        layout.AddRow(topography_groupbox)
        
        # ---------------------------
        # - 'V' Line Path group box -
        vline_groupbox = forms.GroupBox(Text = '\'V\' Path', Padding = 5)
        
        self.vline_gen_button = forms.Button(Text = 'Generate')
        # self.generate_button.Click += self.OnVlineGenButtonClick  TODO!!!
        
        grouplayout = forms.DynamicLayout()
        grouplayout.AddRow(None, self.vline_gen_button, None)
        vline_groupbox.Content = grouplayout
        
        layout.AddRow(vline_groupbox)
        
        # ---------------------------
        # - G-code group box -
        gcode_groupbox = forms.GroupBox(Text = 'Export', Padding = 5)
        
        self.export_csv_button = forms.Button(Text = '*.csv')
        self.export_gcode_button = forms.Button(Text = '*.gcode')
        self.export_gcode_button.Click += self.OnExportButtonClick
        
        grouplayout = forms.DynamicLayout()
        grouplayout.AddRow(self.export_csv_button,'  ', self.export_gcode_button)
        gcode_groupbox.Content = grouplayout
        
        layout.AddRow(gcode_groupbox)
        
        # = End of group boxes =
        layout.EndVertical()

        # add a logo at the bottom
        logo_image_view = forms.ImageView()
        logo_image_view.Size = drawing.Size(200, 30)
        logo_image_view.Image = drawing.Bitmap(__file__ + '../../img/longeviti.bmp')
        
        layout.BeginVertical()
        layout.AddRow(logo_image_view)
        layout.EndVertical()

        # Create the default button
        self.DefaultButton = forms.Button(Text = 'OK')
        self.DefaultButton.Click += self.OnOKButtonClick

        # Create the abort button
        self.AbortButton = forms.Button(Text = 'Cancel')
        self.AbortButton.Click += self.OnCloseButtonClick

        layout.AddSeparateRow(None, self.DefaultButton, self.AbortButton, None)
        
        self.Content = layout

    # Registration Start button click handler
    def OnRegisterButtonClick(self, sender, e):
        self.status_textbox.Text = 'registration in progress ...'
        registration_dialog = RegistrationDialog()
        Rhino.UI.EtoExtensions.ShowSemiModal(registration_dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        self.status_textbox.Text = 'registration complete'

    # Topography configure button click handler
    def OnTopoConfigButtonClick(self, sender, e):
        self.status_textbox.Text = 'configuring topography...'
        self.topography_configure_dialog = TopographyConfigureDialog()
        self.topography_configure_dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
        [self.topo_gen_mode, self.topo_path_count, self.topo_offset_dist] = self.topography_configure_dialog.OnOKButtonClick(sender, e)
        self.status_textbox.Text = 'configuration complete'

    # Topography generate button click handler
    def OnTopoGenButtonClick(self, sender, e):
        self.status_textbox.Text = 'generating topography path'
        # Select the mesh
        mesh = rs.GetObject("Select mesh", rs.filter.mesh )
        self.topography_path = TopographyPath(mesh, self.topo_path_count, self.topo_offset_dist)
        if self.topo_gen_mode is TOPO_PICK_3_POINTS:
            # Select 3 vertex on the mesh to construct a intersection plane
            pt_1 = rs.GetPointOnMesh(mesh, "Select 1st vertice on mesh for constructing a plane")
            pt_2 = rs.GetPointOnMesh(mesh, "Select 2nd vertice on mesh for constructing a plane")
            pt_3 = rs.GetPointOnMesh(mesh, "Select 3rd vertice on mesh for constructing a plane")
            self.polyline_point_array = self.topography_path.generatePolylineFrom3Pts(pt_1, pt_2, pt_3)
        elif self.topo_gen_mode is TOPO_PICK_TOP_POINT:
           # Select a top vertice on the mesh to construct a plane normal
           mesh_top_pt = rs.GetPointOnMesh(mesh, "Select a top vertice on mesh")
           self.polyline_point_array = self.topography_path.generatePolylineFromCentroidTopPt(mesh_top_pt)
        else:
            pass
        result = rs.LastCommandResult()
        if result == 0:
            self.status_textbox.Text = 'path generated'
        else:
            self.status_textbox.Text = 'unsuccessful'
    
    
    # G-code Export button click handler
    def OnExportButtonClick(self, sender, e):
        self.status_textbox.Text = 'Gcode conversion'
        self.topography_path.exportPolylineGcode(self.polyline_point_array)
        self.status_textbox.Text = 'Gcode exported'

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.status_textbox.Text = ""
        self.Close(False)

    # Close button click handler
    def OnOKButtonClick(self, sender, e):
        self.Close(True)


class TopographyConfigureDialog(forms.Dialog[bool]):
    
    def __init__(self):
        self.Title = 'Topography Path'
        self.Paddomg = drawing.Padding(5)
        self.Resizable = True
        
        # define two global constants
        global TOPO_PICK_3_POINTS
        global TOPO_PICK_TOP_POINT
        TOPO_PICK_3_POINTS = 0
        TOPO_PICK_TOP_POINT = 1
        
        # intersection plane creation mode
        mode_label = forms.Label(Text = 'Mode: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.mode_combobox = forms.ComboBox()
        self.mode_combobox.ReadOnly = True
        self.mode_combobox.DataStore = ['pick 3 points', 'pick top point only']
        self.mode_combobox.SelectedIndex = TOPO_PICK_3_POINTS
        
        # number of path to generate
        path_count_label = forms.Label(Text = 'Layers: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.path_count_stepper = forms.NumericStepper(Value = 10)
        self.path_count_stepper.MinValue = 1

        # offset distance between layers
        offset_dist_label = forms.Label(Text = 'Distance: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.offset_dist_stepper = forms.NumericStepper(Value = 3)
        self.offset_dist_stepper.MinValue = 0
        self.offset_dist_stepper.Increment = 0.5
        self.offset_dist_stepper.DecimalPlaces = 2
        self.offset_dist_stepper.MaximumDecimalPlaces = 4

        # Create the default button
        self.DefaultButton = forms.Button(Text = 'OK')
        self.DefaultButton.Click += self.OnOKButtonClick

        # Create the abort button
        self.AbortButton = forms.Button(Text = 'Cancel')
        self.AbortButton.Click += self.OnCloseButtonClick

        layout = forms.DynamicLayout(Padding = drawing.Padding(5, 5), DefaultSpacing = drawing.Size(2,2))
        
        layout.BeginVertical()
        
        layout.AddRow(mode_label, self.mode_combobox)
        layout.AddRow(path_count_label, self.path_count_stepper)
        layout.AddRow(offset_dist_label, self.offset_dist_stepper)
        
        layout.EndVertical()
        layout.BeginVertical()
        layout.AddRow(None, self.DefaultButton, self.AbortButton, None)
        layout.EndVertical()
        self.Content = layout

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.Close(False)

    # Close button click handler
    def OnOKButtonClick(self, sender, e):
        self.Close(True)
        return [self.mode_combobox.SelectedIndex, int(self.path_count_stepper.Value), self.offset_dist_stepper.Value]


# The script that will be using the dialog.
def openPathDialog():
    dialog = PathDialog();
    # Use Semi-Modal instead to allow interaction with Rhino Document
    rc = Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
#    rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    if (rc):
        print 'Thanks for using Laser Path Generation'

##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if __name__ == "__main__":
    openPathDialog()