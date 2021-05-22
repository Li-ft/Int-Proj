import json
import os
ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
# how it works:
# give a GeoJSON containing polygons or multipolygons(which wll be split in polygons)
# output will be a list of polygon coordinates
# -optionally a dict of format:
#   prop_data = {"property_name": str, "building_type": {"b_type": property_val, "b_type2": ..}}
#   output will be a dict of format {"b_type1": coordlist1, "b_type2": coordlist2};
#   where the value of b_type is a list of coordinates of the Polygons which
#   had the property: prop_data["property_name"] = prop_data["b_type"]


class GeoJSONReader:
    # GeoJSON types: "Feature", "FeatureCollection", "geometry types"
    # geometry types: "Point", "MultiPoint", "LineString",
    #       "MultiLineString", "Polygon", "MultiPolygon", and
    #       "GeometryCollection".
    # for an example see: "GeoJSON_example.json"

    # loaded must be a GeoJSON file following the RFC 7946 standard

    def __init__(self):
        self.data_dict = None
        self.features = None

    def read_GeoJSON(self, filename, property_data=None):
        with open(filename, "r") as fp:
            self.data_dict = json.load(fp)
        # 1st level
        if "FeatureCollection" == self.data_dict["type"]:
            self.features = self.data_dict["features"]
        else:
            raise KeyError("1st level is not a FeatureCollection")
        if property_data is None:
            output = []
            for el in self.features:
                geom = el["geometry"]
                if geom["type"] == "Polygon":
                    # append polygon's coordinate list
                    output.append(geom["coordinates"][0])
                if geom["type"] == "MultiPolygon":
                    for polygon in geom["coordinates"]:
                        # append polygon's coordinate list
                        output.append(polygon[0])
            return output
        if property_data is not None:
            return self.group_buildings(property_data)

    def group_buildings(self, prop_data):
        # -optionally a dict of format:
        #   prop_data = {"property_name": str, "building_type": {"b_type": property_val, "b_type2": ..}}
        #   output will be a dict of format {"b_type1": coordlist1, "b_type2": coordlist2};
        #   where the value of b_type is a list of coordinates of the Polygons which
        #   had the property: prop_data["property_name"] = prop_data["b_type"]
        # ex: {"property_name": "prop0", "building_type": {"house": "value0", "work": "value1"}}
        prop_name = prop_data["property_name"]
        building_types = prop_data["building_type"]
        output = {}
        for b_type in building_types.keys():
            output[b_type] = []
        for el in self.features:
            prop = el["properties"]
            if prop_name in prop.keys():
                if prop[prop_name] in building_types.values():
                    geom = el["geometry"]
                    if geom["type"] == "Polygon":
                        for b_type in building_types.keys():
                            if prop[prop_name] == building_types[b_type]:
                                # append polygon's coordinate list
                                output[b_type].append(geom["coordinates"])
                    if geom["type"] == "MultiPolygon":
                        for polygon in geom["coordinates"]:
                            for b_type in building_types.keys():
                                if prop[prop_name] == building_types[b_type]:
                                    # append polygon's coordinate list
                                    output[b_type].append(polygon[0])
        return output

    def get_json_keys(self):
        return self.data_dict.keys()

    def get_data_dict(self):
        return self.data_dict


if __name__ == "__main__":
    fileName = ABSOLUTE_PATH+r"\geo_data\custom.geo.json"
    fileName2 = ABSOLUTE_PATH + r"\GeoJSON_example.json"
    prop_test = {"property_name": "prop0", "building_type": {"house": "value0", "work": "value1"}}
    testR = GeoJSONReader()
    data = testR.read_GeoJSON(fileName2, prop_test)
    # data = testR.get_data_dict()
    print("bruh")