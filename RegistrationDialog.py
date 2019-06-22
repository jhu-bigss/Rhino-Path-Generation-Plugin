################################################################################
# RegistrationDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import scriptcontext
import rhinoscriptsyntax as rs
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

################################################################################
# Sample dialog class extending the Eto Dialog([T])
################################################################################
class RegistrationDialog(forms.Dialog[bool]): # return True or False from ShowModal()

    def __init__(self):
        self.Title = "Implant Points Registraion"
        self.Resizable = False
        self.Padding = drawing.Padding(5)

        # Points Count for registration algorithm
        self.PtsCountStepper = forms.NumericStepper()
        self.PtsCountStepper.MinValue = 4
        self.PtsCountStepper.ValueChanged += self.ptsCountStepperValueChanged

       # Custom label helper to set alignment
        def L(text):
            m_label = forms.Label()
            m_label.Text = text
            m_label.VerticalAlignment = forms.VerticalAlignment.Center
            m_label.TextAlignment = forms.TextAlignment.Right
            return m_label

        # set content of the collapsed section
        self.collapsePanel = forms.DynamicLayout(Visible = False, Padding = drawing.Padding(40, 10), DefaultSpacing = drawing.Size(5, 5))
        self.collapsePanel.BeginVertical()
        
        # list coordinates of collect points in a TreeGridView
        self.coord_treegridview = forms.TreeGridView()
        self.coord_treegridview.Size = drawing.Size(200, 200)
        
        column0 = forms.GridColumn()
        column0.HeaderText = 'Point'
        column0.DataCell = forms.TextBoxCell(0)
        self.coord_treegridview.Columns.Add(column0)

        column1 = forms.GridColumn()
        column1.HeaderText = 'X'
        column1.Editable = True
        column1.DataCell = forms.TextBoxCell(1)
        self.coord_treegridview.Columns.Add(column1)
        
        column2 = forms.GridColumn()
        column2.HeaderText = 'Y'
        column2.Editable = True
        column2.DataCell = forms.TextBoxCell(2)
        self.coord_treegridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = 'Z'
        column3.Editable = True
        column3.DataCell = forms.TextBoxCell(3)
        self.coord_treegridview.Columns.Add(column3)
        
        # Initialize table content
        self.updateTreeGridContent()
        
        self.collapsePanel.AddRow(None, self.coord_treegridview)
        self.collapsePanel.EndVertical()
#        self.collapsePanel.BeginVertical()
#        self.collapsePanel.AddRow(None, forms.CheckBox(Text = "Refine mesh"))
#        self.collapsePanel.AddRow(None, forms.CheckBox(Text = "Jagged seams"), forms.CheckBox(Text = "Pack textures"), None)
#        self.collapsePanel.AddRow(None, forms.CheckBox(Text = "Simple planes"))
#        self.collapsePanel.EndVertical()

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
        self.updateTreeGridContent(int(self.PtsCountStepper.Value))

    def updateTreeGridContent(self, pts_count = 4):
        """update the table content"""
        treecollection = forms.TreeGridItemCollection()
        item_machine = forms.TreeGridItem(Values=('machine',None,None,None))
        item_machine.Expanded = True
        item_implant = forms.TreeGridItem(Values=('implant',None,None,None))
        item_implant.Expanded = True
        for i in range(pts_count):
            item_machine.Children.Add(forms.TreeGridItem(Values=(i+1,None, None, None)))
            item_implant.Children.Add(forms.TreeGridItem(Values=(i+1,None, None, None)))
        treecollection.Add(item_machine)
        treecollection.Add(item_implant)
        self.coord_treegridview.DataStore = treecollection
        self.coord_treegridview.ReloadData()

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
    dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
    
################################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
################################################################################
if __name__ == "__main__":
    OpenRegistrationDialog()    