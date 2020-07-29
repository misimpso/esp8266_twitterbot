import json

data = '{"ok":69,"wow":[{"a":1},{"a":2},{"a":3}],"cool":{"yep":123}}'

class ParseJson:

    def __init__(self, filter_map):
        self.filter_map = filter_map

    def read(self, amount):
        if not hasattr(self, 'read_counter'):
            self.read_counter = 0
        v = data[self.read_counter:self.read_counter + amount]
        self.read_counter += amount
        return v

    def parse_key(self, keys):
        read_key = self.parse_string()
        if read_key in keys:
            self.read(1)
            return read_key
        return None

            # print("PARSE KEY : {}".format(read_data))
            # while key_i < len(keys) and char_i < len(keys[key_i]):
            #     if keys[key_i][char_i] != read_data:
            #         keys.pop(key_i)
            #         char_i = 0
            #         key_i += 1
            #     else:
            #         char_i += 1
        # while keys_left and read_data != '"':
        #     print("PARSE KEY : {}".format(read_data))
        #     for key_left in keys_left:
        #         if key_left[key_i] != read_data:
        #             print("  KEY LEFT : {}".format(key_left))
        #             print("  KEY I : {}".format(key_i))
        #             keys = keys[key_i+1:] + keys[key_i+1:]
        #             print("  KEYS     : {}".format(keys))
        #     keys_left = keys
        #     read_data = self.read(1)
        #     key_i += 1
        # if len(keys_left) != 1:
        #     return None
        # return keys_left[0]

    def parse_string(self):
        result = []
        while True:
            read_data = self.read(1)
            if read_data in ('"', ''):
                return "".join(result)
            result.append(read_data)

    def parse_group(self, start_char = None):
        symbol_open = {"{": 0, "[": 0, "(": 0}
        symbol_term = {"}", "]", ")"}
        symbol_open[start_char] += 1

        print("START CHAR : {}".format(start_char))
        result = [start_char]
        while True:
            read_data = self.read(1)
            print("PARSE GROUP : `{}` [{}]".format(read_data, symbol_open))
            if read_data == "":
                raise Exception("Reach end of parse group : {}".format(symbol_open))
            result.append(read_data)
            if read_data in symbol_open:
                symbol_open[read_data] += 1
            if read_data in symbol_term:
                if read_data == "}": symbol_open["{"] -= 1
                elif read_data == "]": symbol_open["["] -= 1
                elif read_data == ")": symbol_open["("] -= 1
                if all([symbol_open[s] == 0 for s in symbol_open]):
                    return "".join(result)

    def parse_list(self):
        return "zippy"

    def parse_value(self, value_map = None, skip = False):
        read_data = self.read(1)

        if read_data == '"':
            return self.parse_string()
        elif read_data in ("{", "[", "("):
            if skip or value_map is True:
                return json.loads(self.parse_group(start_char=read_data))
            elif read_data == "{":
                return self.parse_dict(value_map)
            else:
                return self.parse_list(read_data)
        else:
            if value_map is True or not skip:
                result = []
                while True:
                    print("PARSE VALUE X : `{}`".format(read_data))
                    if read_data in (",", '', "}"):
                        return "".join(result)
                    result.append(read_data)
                    read_data = self.read(1)
            else:
                while True:
                    if read_data in (",", '', "}"):
                        return
                    read_data = self.read(1)

    def parse_dict(self, filter_map):

        keys_left = list(filter_map.keys())
        result = {}
        selected_key = None
        read_data = self.read(1)

        while read_data != "":
            print("MAIN READ : `{}`".format(read_data))
            if read_data == '"':

                selected_key = self.parse_key(keys_left)
                print("SELECTED KEY : `{}`".format(selected_key))

                if selected_key is not None:
                    result[selected_key] = self.parse_value(value_map=filter_map[selected_key])

                    # if filter_map[selected_key] is True:
                    #     result[selected_key] = self.parse_true()
                    # else:
                    #     result[selected_key] = self.
                        # read_data = self.read(1)
                        # if read_data == "[" and isinstance(filter_map[selected_key], list):
                        #     combined_keys = {}
                        #     for item in filter_map[selected_key]:
                        #         combined_keys.update(item)
                        #     result[selected_key] = self.parse_list(combined_keys)
                        # elif read_data == "{" and isinstance(filter_map[selected_key], dict):
                        #     result[selected_key] = self.parse_dict(filter_map[selected_key])
                    print("-" * 20)
                    keys_left.remove(selected_key)
                    selected_key = None
                else:
                    self.parse_value(skip=True)
                    

                # while keys_left and selected_key is not None:

                    # if filter_map[selected_key] is True:
                    #     result[selected_key] = self.parse_true()
                    # else:
                    #     read_data = self.read(2)
                    #     if read_data == ":[" and isinstance(filter_map[selected_key], list):
                    #         combined_keys = {}
                    #         for item in filter_map[selected_key]:
                    #             combined_keys.update(item)
                    #         result[selected_key] = self.parse_list(combined_keys)
                    #     elif read_data == ":{" and isinstance(filter_map[selected_key], dict):
                    #         result[selected_key] = self.parse_dict(filter_map[selected_key])

                    # print("-" * 20)
                    # keys_left.remove(selected_key)
                    # selected_key = self.parse_key(keys_left)

                if not keys_left:
                    return result                
            if read_data == "}":
                return result
            read_data = self.read(1)
        return result

if __name__ == "__main__":

    filter_map = {"wow": True, "cool": {"yep": True}}

    print(data)
    pj = ParseJson(filter_map)
    print(pj.parse_dict(filter_map))


        

            

