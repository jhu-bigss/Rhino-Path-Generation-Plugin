################################################################################
# PathDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

from RegistrationDialog import RegistrationDialog

class PathDialog(forms.Dialog[bool]):

    # initialiazation
    def __init__(self):
        self.Title = 'Laser Path Generation'
        self.Paddomg = drawing.Padding(5)
        self.Resizable = False

        # Status text box
        status_label = forms.Label(Text = 'Status: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.status_textbox = forms.TextBox(Text = 'Get Started', TextAlignment = forms.TextAlignment.Center)
        self.status_textbox.ReadOnly = True

        # - Registration group box -
        registration_groupbox = forms.GroupBox(Text = 'Registration', Padding = 5)
        grouplayout = forms.DynamicLayout()
        
        self.register_button = forms.Button(Text = 'Register')
        self.register_button.Click += self.OnRegisterButtonClick
        
        self.apply_button = forms.Button(Text = 'Apply')
        self.apply_button.Click += self.OnApplyButtonClick
        
        grouplayout.AddRow(self.register_button,' ', self.apply_button)
        registration_groupbox.Content = grouplayout
        # ---------------------------

        # - Topography Path group box -
        topography_groupbox = forms.GroupBox(Text = 'Topography Path', Padding = 5)
        grouplayout = forms.DynamicLayout()
        
        self.configure_button = forms.Button(Text = 'Configure')
        self.configure_button.Click += self.OnConfigureButtonClick
        
        self.generate_button = forms.Button(Text = 'Generate')
        self.generate_button.Click += self.OnGenerateButtonClick
        
        grouplayout.AddRow(self.configure_button,' ', self.generate_button)
        topography_groupbox.Content = grouplayout
        # ---------------------------
        
        # - G-code group box -
        gcode_groupbox = forms.GroupBox(Text = 'G-code Conversion', Padding = 5)
        grouplayout = forms.DynamicLayout()
        
        self.convert_button = forms.Button(Text = 'Convert')
        self.convert_button.Click += self.OnConvertButtonClick
        
        self.export_button = forms.Button(Text = 'Export')
        self.export_button.Click += self.OnExportButtonClick
        
        grouplayout.AddRow(self.convert_button,' ', self.export_button)
        gcode_groupbox.Content = grouplayout
        # ---------------------------

        # add a logo at the bottom
        logo_image_view = forms.ImageView()
        logo_image_view.Size = drawing.Size(200, 30)
        logo_image_view.Image = drawing.Bitmap(__file__ + '../../img/longeviti.bmp')

        # Create the default button
        self.DefaultButton = forms.Button(Text = 'OK')
        self.DefaultButton.Click += self.OnOKButtonClick

        # Create the abort button
        self.AbortButton = forms.Button(Text = 'Cancel')
        self.AbortButton.Click += self.OnCloseButtonClick

        # -- Window Layout --
        layout = forms.DynamicLayout(Padding = drawing.Padding(10, 5), DefaultSpacing = drawing.Size(2,2))

        layout.BeginVertical()
        layout.AddRow(status_label, self.status_textbox)
        layout.EndVertical()
        
        layout.BeginVertical()
        layout.AddRow(registration_groupbox)
        layout.AddRow(topography_groupbox)
        layout.AddRow(gcode_groupbox)
        layout.EndVertical()
        
        layout.BeginVertical()
        layout.AddRow(logo_image_view)
        layout.EndVertical()
        
        layout.AddSeparateRow(None, self.DefaultButton, self.AbortButton, None)
        self.Content = layout

    # Registration Start button click handler
    def OnRegisterButtonClick(self, sender, e):
        self.status_textbox.Text = 'registration in progress ...'
        self.registration_dialog = RegistrationDialog()
        Rhino.UI.EtoExtensions.ShowSemiModal(self.registration_dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
        temp = self.registration_dialog.onOkButton_Click(sender, e)
        print temp
        
        self.status_textbox.Text = 'registration complete'

    # Registration Apply button click handler
    def OnApplyButtonClick(self, sender, e):
        self.status_textbox.Text = 'transformation applied'

    # Topography Generate button click handler
    def OnConfigureButtonClick(self, sender, e):
        self.status_textbox.Text = 'configuring...'
        self.topography_configure_dialog = TopographyConfigureDialog()
        self.topography_configure_dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
        temp = self.topography_configure_dialog.OnOKButtonClick(sender, e)
        print temp
        self.status_textbox.Text = 'configuration complete'

    # Topography Preview button click handler
    def OnGenerateButtonClick(self, sender, e):
        self.status_textbox.Text = 'topography path generated'

    # G-code Generate button click handler
    def OnConvertButtonClick(self, sender, e):
        self.status_textbox.Text = 'Gcode generated'

    # G-code Export button click handler
    def OnExportButtonClick(self, sender, e):
        self.status_textbox.Text = 'Gcode exported'

    # Close button click handler
    def OnCloseButtonClick(self, sender, e):
        self.status_textbox.Text = ""
        self.Close(False)

    # Close button click handler
    def OnOKButtonClick(self, sender, e):
        self.Close(True)
        


class TopographyConfigureDialog(forms.Dialog[bool]):

    # initialiazation
    def __init__(self):
        self.Title = 'Topography Path'
        self.Paddomg = drawing.Padding(5)
        self.Resizable = True
        
        # intersection plane creation mode
        mode_label = forms.Label(Text = 'Mode: ', VerticalAlignment = forms.VerticalAlignment.Center, TextAlignment = forms.TextAlignment.Right)
        self.mode_combobox = forms.ComboBox()
        self.mode_combobox.DataStore = ['pick 3 points', 'pick top point only']
        self.mode_combobox.SelectedIndex = 0
        
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
        return [self.mode_combobox.SelectedIndex, self.path_count_stepper.Value, self.offset_dist_stepper.Value]

# The script that will be using the dialog.
def testPathDialog():
    dialog = PathDialog();
    rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    if (rc):
        print 'OK'

##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if __name__ == "__main__":
    testPathDialog()