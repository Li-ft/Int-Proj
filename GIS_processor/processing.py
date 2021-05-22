from GIS_processor.GeoJSON_reader import GeoJSONReader
from shapely.geometry import Polygon
from tools.shapely_func import save_building_shapes_to_file


class GEOProcessor:

    def __init__(self):
        self.GeoJSON_reader = GeoJSONReader()

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

    def store_building_shapes(self):
        pass

