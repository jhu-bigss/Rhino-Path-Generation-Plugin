################################################################################
# RegistrationDialog.py
# Copyright (c) 2019 Joshua Liu
################################################################################
import rhinoscriptsyntax as rs
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms

from compas.utilities import XFunc

from Robot import Robot

################################################################################
# Points Registration dialog class extending the Eto Dialog([T])
################################################################################
class RegistrationDialog(forms.Dialog[bool]):

    def __init__(self):
        self.Title = "Points Registraion"
        self.Resizable = False
        self.Padding = drawing.Padding(5)

        # Stepper Points Count for registration algorithm
        self.pts_count_stepper = forms.NumericStepper()
        self.pts_count_stepper.MinValue = 4
        self.pts_count_stepper.ValueChanged += self.ptsCountStepperValueChanged
        self.reg_pts_count = int(self.pts_count_stepper.Value)

        # set content of the collapsed section
        self.collapsePanel = forms.DynamicLayout(Visible = False, Padding = drawing.Padding(40, 10), DefaultSpacing = drawing.Size(5, 5))
        self.collapsePanel.BeginVertical()
        
        # --- machine grid view ---
        machine_groupbox = forms.GroupBox(Text = 'Collected Points (Workspace)')
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
        for i in range(self.reg_pts_count):
            self.machine_pts_array.append([i+1, None, None, None])

        # update grid view data
        self.machine_pts_gridview.DataStore = self.machine_pts_array
        
        # put everything into machine group layout
        machine_grouplayout.AddRow(None, self.machine_pts_gridview)
        self.sensor_pts_load_button = forms.Button(Text = 'Input Sensor Data')
        self.sensor_pts_load_button.Click += self.sensorLoadButton_Click
        machine_grouplayout.AddRow(None, self.sensor_pts_load_button)
        machine_groupbox.Content = machine_grouplayout
        self.collapsePanel.AddRow(None, machine_groupbox)
        
        # --- mesh grid view ---
        mesh_groupbox = forms.GroupBox(Text = 'Selected Mesh Points')
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
        for i in range(self.reg_pts_count):
            self.mesh_pts_array.append([i+1, None, None, None])
        
        # update grid view data
        self.mesh_pts_gridview.DataStore = self.mesh_pts_array
        
        # put everything into mesh group layout
        mesh_grouplayout.AddRow(None, self.mesh_pts_gridview)
        self.mesh_pts_select_button = forms.Button(Text = 'Select On Mesh')
        self.mesh_pts_select_button.Click += self.meshSelectButton_Click
        mesh_grouplayout.AddRow(None, self.mesh_pts_select_button)
        mesh_groupbox.Content = mesh_grouplayout
        self.collapsePanel.AddRow(None, mesh_groupbox)
        
        self.collapsePanel.EndVertical()

        # button to toggle collapsing
        self.collapseButton = forms.Button(Text = "v", MinimumSize = drawing.Size.Empty)
        self.collapseButton.Click += self.collapseButton_Click
        
        # a few buttons always shown at the bottom
        self.cancelButton = forms.Button(Text = "Cancel")
        self.cancelButton.Click += self.onCancelButton_Click;

        self.okButton = forms.Button(Text = "OK")
        self.okButton.Click += self.onOkButton_Click
        
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
        layout.AddSeparateRow(None, L("Correspondence points "), self.pts_count_stepper, None, self.collapseButton)
        layout.AddCentered(self.collapsePanel) # we need this auto-sized so we can get its width to adjust form height
        layout.Add(None); # expanding space, in case you want the form re-sizable
        layout.AddSeparateRow(None, self.cancelButton, self.okButton);

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

    def ptsCountStepperValueChanged(self, sender, e):
        """update the table content whenever point counts modified"""
        # Input: gridview object, data points array, current number of points
        count_now = int(self.pts_count_stepper.Value)
        count_difference = count_now - self.reg_pts_count
        self.updateGridItem(self.machine_pts_gridview, self.machine_pts_array, count_difference)
        self.updateGridItem(self.mesh_pts_gridview, self.mesh_pts_array, count_difference)
        self.reg_pts_count = count_now

    def updateGridItem(self, gridview_obj, data_array, difference = 0):
        """update point arrays in the grid view table content"""
        counter = self.reg_pts_count
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

    def sensorLoadButton_Click(self, sender, e):
        self.sensor_dialog = SensorDialog(self.reg_pts_count)
        self.sensor_dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
        self.machine_pts_gridview.DataStore = self.sensor_dialog.onOkButton_Click(sender, e)

    def meshSelectButton_Click(self, sender, e):
        # Select the mesh
        mesh = rs.GetObject("Select mesh", rs.filter.mesh )
        for i in range(self.reg_pts_count):
            # pick point on the mesh
            selected_point = rs.GetPointOnMesh(mesh, "Pick registration point " + str(i+1))
            self.mesh_pts_array[i] = [i+1, selected_point.X, selected_point.Y, selected_point.Z]
        # Update grid content
        self.updateGridItem(self.mesh_pts_gridview, self.mesh_pts_array)

    def onCancelButton_Click (self, sender, e):
        self.Close(False)

    def onOkButton_Click (self, sender, e):
        # self.test_rigid_transform_3D()
        self.Close(True)
    
    def rigid_transform_3D(self, A, B):
        # Input: expects Nx3 matrix of points
        # Returns R,t
        # R = 3x3 rotation matrix
        # t = 1x3 row vector
        add = XFunc("numpy.add")
        subtract = XFunc("numpy.subtract")
        linalg_svd = XFunc('numpy.linalg.svd')
        dot = XFunc("numpy.dot")
        transpose = XFunc("numpy.transpose")
        det = XFunc('numpy.linalg.det')
        mean = XFunc('numpy.mean')
        
        assert len(A) == len(B)
        N = len(A) # total points
    
        centroid_A = mean(A, axis=0)
        centroid_B = mean(B, axis=0)
        
        # centre the points
        AA = subtract(A, centroid_A)
        BB = subtract(B, centroid_B)
        
        # dot is matrix multiplication for array
        H = dot(transpose(AA),BB)
        U, S, Vt = linalg_svd(H)
        # R = Vt.T * U.T
        R = dot(transpose(Vt),transpose(U))
    
        # special reflection case
        if det(R) < 0:
           print "Reflection detected"
           Vt[2][:] = [x*-1 for x in Vt[2]]
           R = dot(transpose(Vt),transpose(U))
    
        # t = -R*centroid_A.T + centroid_B.T
        t = subtract(transpose(centroid_B), dot(R, transpose(centroid_A)) )
    
        return R, t
    
    def test_rigid_transform_3D(self):
        # import some Numpy functions
        add = XFunc("numpy.add")
        subtract = XFunc("numpy.subtract")
        multiply = XFunc("numpy.multiply")
        rand = XFunc('numpy.random.rand')
        linalg_svd = XFunc('numpy.linalg.svd')
        dot = XFunc("numpy.dot")
        transpose = XFunc("numpy.transpose")
        det = XFunc('numpy.linalg.det')
        sum = XFunc("numpy.sum")
        sqrt = XFunc("numpy.sqrt")
        
        # Random rotation and translation
        R = rand(3,3)
        t = rand(3)
        
        # make R a proper rotation matrix, force orthonormal
        U, S, Vt = linalg_svd(R)
        R = dot(transpose(Vt),transpose(U))
        
        # remove reflection
        if det(R) < 0:
           Vt[2][:] = [x*-1 for x in Vt[2]]
           R = dot(transpose(Vt),transpose(U))
        
        # number of points
        n = 10
        
        A = rand(n,3)
    
        # B = R * A + t
        B = add(transpose(dot(R, transpose(A))), t)
        
        # recover the transformation
        ret_R, ret_t = self.rigid_transform_3D(A, B)
        
        A2 = add(transpose(dot(ret_R, transpose(A))), ret_t)
        
        # Find the error
        err = subtract(A2,B)
        
        err = multiply(err, err)
        err = sum(err)
        rmse = sqrt(err/n)
        
        print "Points A"
        print A
        print ""
        
        print "Points B"
        print B
        print ""
        
        print "Rotation"
        print R
        print ""
        
        print "Translation"
        print t
        print ""
        
        print "RMSE:", rmse
        print "If RMSE is near zero, the function is correct!"

################################################################################
# Sensor Fiducial Points Input dialog class extending the Eto Dialog([T])
################################################################################
class SensorDialog(forms.Dialog[bool]):
    
    def __init__(self, reg_pts_count = 4):
        self.reg_pts_count = reg_pts_count

        self.Title = "ODmini Dialog"
        self.Resizable = False
        self.Padding = drawing.Padding(5)

        # --- joints grid view ---
        data_input_groupbox = forms.GroupBox(Text = 'Input Sensor Measurements:')
        data_input_grouplayout = forms.DynamicLayout()
         
        # list coordinates of collect points in a TreeGridView
        self.data_gridview = forms.GridView()
        self.data_gridview.ShowHeader = True
        self.data_gridview.Size = drawing.Size(200, 100)
        
        column0 = forms.GridColumn()
        column0.HeaderText = 'ID'
        column0.DataCell = forms.TextBoxCell(0)
        self.data_gridview.Columns.Add(column0)

        column1 = forms.GridColumn()
        column1.HeaderText = 'X'
        column1.Editable = True
        column1.Width = 35
        column1.DataCell = forms.TextBoxCell(1)
        self.data_gridview.Columns.Add(column1)
        
        column2 = forms.GridColumn()
        column2.HeaderText = 'Y'
        column2.Editable = True
        column2.Width = 35
        column2.DataCell = forms.TextBoxCell(2)
        self.data_gridview.Columns.Add(column2)

        column3 = forms.GridColumn()
        column3.HeaderText = 'Z'
        column3.Editable = True
        column3.Width = 35
        column3.DataCell = forms.TextBoxCell(3)
        self.data_gridview.Columns.Add(column3)
        
        column4 = forms.GridColumn()
        column4.HeaderText = 'distance'
        column4.Editable = True
        column4.Width = 35
        column4.DataCell = forms.TextBoxCell(4)
        self.data_gridview.Columns.Add(column4)
        
        
        # Initialize table content
        self.data_array =[]
        for i in range(self.reg_pts_count):
#            self.data_array.append([i+1, None, None, None, None])
            self.data_array.append([i+1, 10, 10, 10, 10])

        # update grid view data
        self.data_gridview.DataStore = self.data_array

        # put everything into group layout
        data_input_grouplayout.AddRow(self.data_gridview)
        data_input_groupbox.Content = data_input_grouplayout
        
        
        self.cancelButton = forms.Button(Text = "Cancel")
        self.cancelButton.Click += self.onCancelButton_Click;

        self.okButton = forms.Button(Text = "OK")
        self.okButton.Click += self.onOkButton_Click
        
        # set default buttons when user presses enter or escape anywhere on the form
        self.DefaultButton = self.okButton
        self.AbortButton = self.cancelButton
        
        # App main layout
        layout = forms.DynamicLayout(DefaultSpacing = drawing.Size(2,2))
        layout.AddCentered(data_input_groupbox) # we need this auto-sized so we can get its width to adjust form height
        layout.Add(None); # expanding space, in case you want the form re-sizable
        layout.AddSeparateRow(None, self.cancelButton, self.okButton);

        self.Content = layout;

    def convertDataToWorkCoordinates(self):
        # new robot-class object
        robot = Robot()

        # Convert data array into float
        data_grid_float = []
        for row in self.data_gridview.DataStore:
            data_grid_float.append([float(i) for i in row[1:]])
        
        # Compute workpiece coordinates for each data set
        data_array_work_coordinates = []
        id_index = 1
        for data_set in data_grid_float:
            data_work_coordinates = robot.getWorkPtPosFromSensorJoints(data_set)
            data_work_coordinates.insert(0, id_index)
            data_array_work_coordinates.append(data_work_coordinates)
            id_index += 1

        return data_array_work_coordinates

    def onOkButton_Click (self, sender, e):
        self.Close(True)
        return self.convertDataToWorkCoordinates()

    def onCancelButton_Click (self, sender, e):
        self.Close(False)


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