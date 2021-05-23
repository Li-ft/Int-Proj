from GIS_processor.GeoJSON_reader import GeoJSONReader
from shapely.geometry import Polygon
from tools.shapely_func import save_building_shapes_to_file

# INTERFACE COMMANDS:
# loadGeoJSON -d filename


class GEOProcessor:

    def __init__(self):
        self.GeoJSON_reader = GeoJSONReader()
        self.building_data = {}

    def load_shapes_from_GeoJSON(self, filename, GeoJSON_property_data = None):
        coords = self.GeoJSON_reader.read_GeoJSON(filename, GeoJSON_property_data)
        if GeoJSON_property_data is None:
            # coords is a list of coordinate pairs
            return [Polygon(coord) for coord in coords]
        else:
            # coords is a dict of format {"building_type: [coords_b1,coords_b2,.]"}
            output_dict = {}
            for b_type in coords.keys():
                output_dict[b_type] = []
                for coord in coords[b_type]:
                    output_dict[b_type].append(coord)
            return output_dict

    def generate_sim_space_from_GeoJSON(self, file_data):
        # different files can be loaded at once
        # file data is a dict {"b_type" : {"file_type": FILE_TYPE, "file_name": .., "prop_data":}}
        # b_type should be an acceptable BUILDING_TYPE ("house", "work", etc.)
        # FILE_TYPE can be "simple"->all polygons stored as b_type,
        #   "selective"->data properties expected("prop_data"), see GeoJSON_reader.py
        for building_type in file_data.keys():
            if file_data[building_type]["file_type"] == "simple":
                self.building_data[building_type] = self.load_shapes_from_GeoJSON(file_data[building_type]["file_name"])
            if file_data[building_type]["file_type"] == "selective":
                building_dict = self.load_shapes_from_GeoJSON(file_data[building_type]["file_name"],
                                                              file_data[building_type]["file_name"])
                for b_type in building_dict.keys():
                    self.building_data[b_type] = building_dict[b_type]

    def reset_sim_space(self):
        self.building_data = {}

    def store_sim_space_to_file(self, filename):
        save_building_shapes_to_file(filename, self.building_data)


