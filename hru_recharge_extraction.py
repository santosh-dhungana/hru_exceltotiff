import arcpy, os, sys, glob
from arcpy.conversion import ExcelToTable, TableToTable, FeatureToRaster
from arcpy.management import AddJoin, RemoveJoin, Delete, SelectLayerByAttribute, MakeFeatureLayer, BuildRasterAttributeTable, CompositeBands, MakeTableView
from arcpy import GetParameterAsText as gp


# read table and make temporaty layer


in_table= gp(0)
in_sheet=gp(1)
out_table='temptable'
join_fieldtable = gp(2)

#table_dir=os.path.dirname(in_table)
in_dir = os.path.dirname(in_table)
arcpy.AddMessage(in_dir)
arcpy.env.Workspace= in_dir
arcpy.env.overwriteOutput=True
# define filters
year = gp(3)

start_month= gp(4)
end_month=gp(5)

# input feature/raster to join
in_dataset = gp(6)
join_fieldfeat =gp(7)

# field to extract
field_toextract =gp(8)
cellSize=gp(9)

#annual/monthly
period=gp(10)

#create temporary table
arcpy.AddMessage("Creating temporary table ......")
hrutable = ExcelToTable(in_table, 'temptable', in_sheet)


#new additions 04/11/2021
#hrutable=MakeTableView(in_table=in_table,out_view='viewtemp')

try:
    for month in range(int(start_month), int(end_month)+1):
        where_clause= ' "YEAR" = {0} AND "MON" = {1}'.format(year, month)
        #select attribute
        #selection = SelectLayerByAttribute(hrutable, "NEW_Selection", where_clause)
        #export table to dbf file
        arcpy.AddMessage("Executing table creation .......")
        selected_dbf = TableToTable(hrutable, in_dir, 'temporary.dbf', where_clause)
        
        #join above extracted table to provided feature/raster dataset based on the provided joinfield
        arcpy.AddMessage("Joining table to dataset ......")
        #create feature layer first
        feat_layer = MakeFeatureLayer(in_dataset, 'feat_layer')
        joined_dataset = AddJoin(feat_layer, join_fieldfeat, selected_dbf, join_fieldtable)

        
        # convert feature to raster
        arcpy.AddMessage("Executing feature to raster conversion .....")
        recharge=FeatureToRaster(joined_dataset, "temporary.{0}".format(field_toextract), os.path.join(in_dir, "rec_{0}_{1}.tif".format(year,month)), cellSize)
        #BuildRasterAttributeTable(recharge, "Overwrite")

       
                           
        # remove join
        arcpy.AddMessage("Removing join ....")
        RemoveJoin(joined_dataset, "temporary")

        # delete dbf tables earlier created
        arcpy.AddMessage("Deleting temporary dbf table......")
        Delete(selected_dbf)
            
     # Build raster composite
    raster_for_composite= glob.glob(in_dir +'/rec_*.tif')
    arcpy.AddMessage(raster_for_composite)
    if len(raster_for_composite)>1:
        CompositeBands(raster_for_composite, in_dir+'/{0}.tif'.format(period))
        # delete all temporary rasters
        arcpy.AddMessage("Deleting Temporary Rasters .......")
        for raster in raster_for_composite:
            Delete(raster)      

    
except Exception as e:
    arcpy.AddError(e)
    arcpy.AddMessage(e)





