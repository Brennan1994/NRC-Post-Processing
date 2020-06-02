Sub Add_Series()
'
' Add_Series Macro
'

'
    Dim Row As Integer
    Dim SeriesNum As Integer
    SeriesNum = 1
    Row = 1
    
    'ActiveChart.ChartArea.Clear
    
    For SeriesNum = 1 To 203
    
        ActiveChart.SeriesCollection.NewSeries
        ActiveChart.FullSeriesCollection(SeriesNum).Name = "=Data_Inverse!$A$" & Row
        ActiveChart.FullSeriesCollection(SeriesNum).XValues = "=Data_Inverse!$B$" & Row & ":$SG$" & Row
        Row = Row + 1
        ActiveChart.FullSeriesCollection(SeriesNum).Values = "=Data_Inverse!$B$" & Row & ":$SG$" & Row
        Row = Row + 1
    
    Next SeriesNum
    
    
End Sub


Sub Format_All_Series()
'PURPOSE: How to cycle through charts and chart series

    Dim ser As Series
'Loop through all series in a chart
    For Each ser In ActiveChart.SeriesCollection
        With ser.Format.Line
            .Visible = msoTrue
            .ForeColor.ObjectThemeColor = msoThemeColorAccent1
            .ForeColor.TintAndShade = 0
            .ForeColor.Brightness = 0
            .Transparency = 0.75
        End With
    Next ser
  
End Sub

Sub ClearChart()
'PURPOSE: Clears all series from a chart
    ActiveChart.ChartArea.Clear
End Sub