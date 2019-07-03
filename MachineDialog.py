################################################################################
# MachineDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

#from kinematics import Robot

################################################################################
# Machine Joint Input dialog class extending the Eto Dialog([T])
################################################################################
class MachineFKDialog(forms.Dialog[bool]): # return True or False from ShowModal()

    def __init__(self, reg_pts_count = 4):
        self.RegPtsCount = reg_pts_count

        self.Title = "Input Machine Joints"
        self.Resizable = False
        self.Padding = drawing.Padding(5)

        # --- joints grid view ---
        joint_input_groupbox = forms.GroupBox(Text = 'Machine Joints -> Workspace Points')
        joint_input_grouplayout = forms.DynamicLayout()
         
        # list coordinates of collect points in a TreeGridView
        self.joints_gridview = forms.GridView()
        self.joints_gridview.ShowHeader = True
        self.joints_gridview.Size = drawing.Size(200, 100)
        
        column0 = forms.GridColumn()
        column0.HeaderText = 'ID'
        column0.DataCell = forms.TextBoxCell(0)
        self.joints_gridview.Columns.Add(column0)

        column1 = forms.GridColumn()
        column1.HeaderText = 'X'
        column1.Editable = True
        column1.Width = 35
        column1.DataCell = forms.TextBoxCell(1)
        self.joints_gridview.Columns.Add(column1)
        
        column2 = forms.GridColumn()
        column2.HeaderText = 'Y'
        column2.Editable = True
        column2.Width = 35
        column2.DataCell = forms.TextBoxCell(2)
        self.joints_gridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = 'Z'
        column3.Editable = True
        column3.Width = 35
        column3.DataCell = forms.TextBoxCell(3)
        self.joints_gridview.Columns.Add(column3)
        
        column4 = forms.GridColumn()
        column4.HeaderText = 'B'
        column4.Editable = True
        column4.Width = 35
        column4.DataCell = forms.TextBoxCell(4)
        self.joints_gridview.Columns.Add(column4)
        
        column5 = forms.GridColumn()
        column5.HeaderText = 'C'
        column5.Editable = True
        column5.Width = 35
        column5.DataCell = forms.TextBoxCell(5)
        self.joints_gridview.Columns.Add(column5)
        
        # Initialize table content
        self.joints_array =[]
        for i in range(self.RegPtsCount):
            self.joints_array.append([i+1, None, None, None, None, None])

        # update grid view data
        self.joints_gridview.DataStore = self.joints_array
        
        # put everything into group layout
        joint_input_grouplayout.AddRow(None, self.joints_gridview)
        joint_input_groupbox.Content = joint_input_grouplayout
        
        
        self.cancelButton = forms.Button(Text = "Cancel")
        self.cancelButton.Click += self.cancelButton_Click;

        self.finishButton = forms.Button(Text = "OK")
        self.finishButton.Click += self.finishButton_Click
        
        # set default buttons when user presses enter or escape anywhere on the form
        self.DefaultButton = self.finishButton
        self.AbortButton = self.cancelButton
        
        # App main layout
        layout = forms.DynamicLayout(DefaultSpacing = drawing.Size(2,2))
        layout.AddCentered(joint_input_groupbox) # we need this auto-sized so we can get its width to adjust form height
        layout.Add(None); # expanding space, in case you want the form re-sizable
        layout.AddSeparateRow(None, self.cancelButton, self.finishButton);

        self.Content = layout;

    def cancelButton_Click (self, sender, e):
        self.Close(False)

    def finishButton_Click (self, sender, e):
        self.Close(True)
        return self.joints_gridview.DataStore

################################################################################
# Creating a dialog instance and displaying the dialog.
################################################################################

def OpenMachineFKDialog():
    dialog = MachineFKDialog()
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    
################################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
################################################################################
if __name__ == "__main__":
    OpenMachineFKDialog()