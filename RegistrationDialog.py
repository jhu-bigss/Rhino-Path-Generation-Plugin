################################################################################
# RegistrationDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import scriptcontext
import rhinoscriptsyntax as rs
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

from MachineDialog import MachineFKDialog

################################################################################
# Points Registration dialog class extending the Eto Dialog([T])
################################################################################
class RegistrationDialog(forms.Dialog[bool]):

    def __init__(self):
        self.Title = "Implant Points Registraion"
        self.Resizable = False
        self.Padding = drawing.Padding(5)

        # Stepper Points Count for registration algorithm
        self.PtsCountStepper = forms.NumericStepper()
        self.PtsCountStepper.MinValue = 4
        self.PtsCountStepper.ValueChanged += self.ptsCountStepperValueChanged
        self.RegPtsCount = int(self.PtsCountStepper.Value)

        # set content of the collapsed section
        self.collapsePanel = forms.DynamicLayout(Visible = False, Padding = drawing.Padding(40, 10), DefaultSpacing = drawing.Size(5, 5))
        self.collapsePanel.BeginVertical()
        
        # --- machine grid view ---
        machine_groupbox = forms.GroupBox(Text = 'Machine Points')
        machine_grouplayout = forms.DynamicLayout()
        
        # list coordinates of collect points in a TreeGridView
        self.machine_pts_gridview = forms.GridView()
        self.machine_pts_gridview.ShowHeader = True
        self.machine_pts_gridview.Size = drawing.Size(200, 100)
        
        column0 = forms.GridColumn()
        column0.HeaderText = 'ID'
        column0.DataCell = forms.TextBoxCell(0)
        self.machine_pts_gridview.Columns.Add(column0)

        column1 = forms.GridColumn()
        column1.HeaderText = 'X'
        column1.Editable = True
        column1.Width = 55
        column1.DataCell = forms.TextBoxCell(1)
        self.machine_pts_gridview.Columns.Add(column1)
        
        column2 = forms.GridColumn()
        column2.HeaderText = 'Y'
        column2.Editable = True
        column2.Width = 55
        column2.DataCell = forms.TextBoxCell(2)
        self.machine_pts_gridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = 'Z'
        column3.Editable = True
        column3.Width = 55
        column3.DataCell = forms.TextBoxCell(3)
        self.machine_pts_gridview.Columns.Add(column3)
        
        # Initialize table content
        self.machine_pts_array =[]
        for i in range(self.RegPtsCount):
            self.machine_pts_array.append([i+1, None, None, None])

        # update grid view data
        self.machine_pts_gridview.DataStore = self.machine_pts_array
        
        # put everything into machine group layout
        machine_grouplayout.AddRow(None, self.machine_pts_gridview)
        self.machine_pts_load_button = forms.Button(Text = 'Load Machine Points')
        self.machine_pts_load_button.Click += self.machineLoadButton_Click
        machine_grouplayout.AddRow(None, self.machine_pts_load_button)
        machine_groupbox.Content = machine_grouplayout
        self.collapsePanel.AddRow(None, machine_groupbox)
        
        # --- mesh grid view ---
        mesh_groupbox = forms.GroupBox(Text = 'Mesh Points')
        mesh_grouplayout = forms.DynamicLayout()
        
        # list all the coordinates of collect points in a GridView
        self.mesh_pts_gridview = forms.GridView()
        self.mesh_pts_gridview.ShowHeader = True
        self.mesh_pts_gridview.Size = drawing.Size(200, 100)
        
        column0 = forms.GridColumn()
        column0.HeaderText = 'ID'
        column0.DataCell = forms.TextBoxCell(0)
        self.mesh_pts_gridview.Columns.Add(column0)

        column1 = forms.GridColumn()
        column1.HeaderText = 'X'
        column1.Editable = True
        column1.Width = 55
        column1.DataCell = forms.TextBoxCell(1)
        self.mesh_pts_gridview.Columns.Add(column1)
        
        column2 = forms.GridColumn()
        column2.HeaderText = 'Y'
        column2.Editable = True
        column2.Width = 55
        column2.DataCell = forms.TextBoxCell(2)
        self.mesh_pts_gridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = 'Z'
        column3.Editable = True
        column3.Width = 55
        column3.DataCell = forms.TextBoxCell(3)
        self.mesh_pts_gridview.Columns.Add(column3)
        
        # Initialize table content
        self.mesh_pts_array =[]
        for i in range(self.RegPtsCount):
            self.mesh_pts_array.append([i+1, None, None, None])
        
        # update grid view data
        self.mesh_pts_gridview.DataStore = self.mesh_pts_array
        
        # put everything into mesh group layout
        mesh_grouplayout.AddRow(None, self.mesh_pts_gridview)
        self.mesh_pts_select_button = forms.Button(Text = 'Select Mesh Points')
        self.mesh_pts_select_button.Click += self.meshSelectButton_Click
        mesh_grouplayout.AddRow(None, self.mesh_pts_select_button)
        mesh_groupbox.Content = mesh_grouplayout
        self.collapsePanel.AddRow(None, mesh_groupbox)
        
        self.collapsePanel.EndVertical()

        # button to toggle collapsing
        self.collapseButton = forms.Button(Text = "v", MinimumSize = drawing.Size.Empty)
        self.collapseButton.Click += self.collapseButton_Click
        
        # a few buttons always shown at the bottom
        self.previewButton = forms.Button(Text = "Preview")

        self.cancelButton = forms.Button(Text = "Cancel")
        self.cancelButton.Click += self.cancelButton_Click;

        self.okButton = forms.Button(Text = "OK")
        self.okButton.Click += self.okButton_Click
        
        # set default buttons when user presses enter or escape anywhere on the form
        self.DefaultButton = self.okButton
        self.AbortButton = self.cancelButton
        
        # Custom label helper to set alignment
        def L(text):
            m_label = forms.Label()
            m_label.Text = text
            m_label.VerticalAlignment = forms.VerticalAlignment.Center
            m_label.TextAlignment = forms.TextAlignment.Right
            return m_label
        
        # App main layout
        layout = forms.DynamicLayout(DefaultSpacing = drawing.Size(2,2))
        layout.AddSeparateRow(None, L("Correspondence points "), self.PtsCountStepper, None, self.collapseButton)
        layout.AddCentered(self.collapsePanel) # we need this auto-sized so we can get its width to adjust form height
        layout.Add(None); # expanding space, in case you want the form re-sizable
        layout.AddSeparateRow(None, self.previewButton, self.cancelButton, self.okButton);

        self.Content = layout;


    def collapseButton_Click(self, sender, e):
        if self.collapsePanel.Visible:
           self.ClientSize = drawing.Size(self.ClientSize.Width, self.ClientSize.Height - self.collapsePanel.Height)
           self.collapsePanel.Visible = False
           self.collapseButton.Text = "^"
        else:
           self.collapsePanel.Visible = True
           self.collapseButton.Text = "v"
           self.ClientSize = drawing.Size(max(self.ClientSize.Width, self.collapsePanel.Width), self.ClientSize.Height + self.collapsePanel.Height)
#            except:
#             print "Unexpected error:", sys.exc_info()[0]
#             pass # so we don't bring down rhino if there's a bug in the script

    def ptsCountStepperValueChanged(self, sender, e):
        """update the table content whenever point counts modified"""
        # Input: gridview object, data points array, current number of points
        count_now = int(self.PtsCountStepper.Value)
        count_difference = count_now - self.RegPtsCount
        self.updateGridItem(self.machine_pts_gridview, self.machine_pts_array, count_difference)
        self.updateGridItem(self.mesh_pts_gridview, self.mesh_pts_array, count_difference)
        self.RegPtsCount = count_now

    def updateGridItem(self, gridview_obj, data_array, difference = 0):
        """update point arrays in the grid view table content"""
        counter = self.RegPtsCount
        if difference > 0:
            for i in range(difference):
                counter += 1
                data_array.append([counter, None, None, None])
                gridview_obj.DataStore = data_array
        elif difference < 0:
            for i in range(-difference):
                counter -= 1
                del data_array[-1]
                gridview_obj.DataStore = data_array
        else:
            gridview_obj.DataStore = data_array
            return

    def machineLoadButton_Click(self, sender, e):
        self.Machine_Dialog = MachineFKDialog(self.RegPtsCount)
        self.Machine_Dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
        temp = self.Machine_Dialog.finishButton_Click(sender, e)
        print temp

    def meshSelectButton_Click(self, sender, e):
        # Select the mesh
        mesh = rs.GetObject("Select mesh", rs.filter.mesh )
        for i in range(self.RegPtsCount):
            # pick point on the mesh
            selected_point = rs.GetPointOnMesh(mesh, "Pick registration point " + str(i+1))
            self.mesh_pts_array[i] = [i+1, selected_point.X, selected_point.Y, selected_point.Z]
        # Update grid content
        self.updateGridItem(self.mesh_pts_gridview, self.mesh_pts_array)

    def cancelButton_Click (self, sender, e):
        self.Close(False)

    def okButton_Click (self, sender, e):
        self.Close(True)

        if self.ShowModal():
            print "Do something, user clicked OK"

################################################################################
# Creating a dialog instance and displaying the dialog.
################################################################################

def OpenRegistrationDialog():
    dialog = RegistrationDialog()
    ## dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    # Use Semi-Modal instead to allow interaction with Rhino Document
    Rhino.UI.EtoExtensions.ShowSemiModal(dialog, Rhino.RhinoDoc.ActiveDoc, Rhino.UI.RhinoEtoApp.MainWindow)
    
################################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
################################################################################
if __name__ == "__main__":
    OpenRegistrationDialog()