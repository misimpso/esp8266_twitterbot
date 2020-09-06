import json

# from pprint import pprint


class ParseJson:

    def __init__(self, socket = None):
        self.socket = socket

    def read(self, amount):
        if self.socket is None:
            if not hasattr(self, 'read_counter'):
                self.read_counter = 0
            v = data[self.read_counter:self.read_counter + amount]
            self.read_counter += amount
            return v
        return self.socket.recv(amount).decode()

    def parse_string(self, indent=0):
        result = []
        escaped = False
        while True:
            read_data = self.read(1)
            print("{}PARSE STRING ({}): `{}` {}".format("--" * indent, escaped, read_data, result))
            if read_data == "" or (read_data == '"' and not escaped):
                return "".join(result)
            elif read_data == "\\":
                escaped = True
            else:
                escaped = False
            result.append(read_data)

    def parse_key(self, keys, indent=0):
        read_key = self.parse_string(indent=indent + 1)
        if read_key in keys:
            print("{}PARSE KEY : PASS, `{}` in {}".format("--" * indent, read_key, keys))
            self.read(1)
            return read_key
        print("{}PARSE KEY : FAIL, `{}` not in {}".format("--" * indent, read_key, keys))
        return None

    def extract_obj(self, start_char = None, indent=0):
        symbol_open = {"{": 0, "[": 0}
        symbol_term = {"}": "{", "]": "["}
        symbol_open[start_char] += 1
        print("{}START CHAR : {}".format("--" * indent, start_char))

        result = [start_char]

        while True:
            read_data = self.read(1)
            print("{}PARSE GROUP : `{}` [{}]".format("--" * indent, read_data, symbol_open))
            if read_data == "":
                raise Exception("Reach end of parse group : {}".format(symbol_open))
            result.append(read_data)

            if read_data in symbol_open:
                symbol_open[read_data] += 1

            elif read_data in symbol_term:
                symbol_open[symbol_term[read_data]] -= 1

                if all(s_v <= 0 for s_v in symbol_open.values()):
                    return "".join(result)

    def traverse_list(self, value_map, indent=0):
        bracket_open = 1
        result = ["["]
        while True:
            read_data = self.read(1)
            print("{}PARSE LIST : `{}` {} [ {} ]".format("--" * indent, read_data, bracket_open, " ".join(result)))
            if read_data == "":
                raise Exception("Reach end of traverse list, `{}`".format(result))
            if read_data != "{":
                result.append(read_data)

            if read_data in (",", " "):
                continue
            elif read_data == "[":
                bracket_open += 1
            elif read_data == "]":
                bracket_open -= 1
                if bracket_open <= 0:
                    print("{}RESULT : {}".format("--" * indent, result))
                    return "".join(result)
            else:
                parsed_result, end_char = self.parse_value(start_char=read_data, value_map=value_map, indent=indent + 1)
                result.append(parsed_result)
                if end_char == "]":
                    bracket_open -= 1
                    if bracket_open <= 0:
                        print("{}RESULT : {}".format("--" * indent, result))
                        return "".join(result)


    def traverse_dict(self, filter_map, indent=0):
        brace_open = 1
        keys_left = list(filter_map.keys())
        result = ["{"]

        while True:
            read_data = self.read(1)
            print("{}PARSE DICT (T) : `{}` {} [ {} ]".format("--" * indent, read_data, brace_open, " ".join(result)))
            if read_data == "":
                raise Exception("Reach end of traverse dict, `{}`".format(result))

            if keys_left and read_data == '"':
                parsed_key = self.parse_string(indent=indent + 1)
                print("{}PARSE DICT (1) : (`{}` {} {}) <[ {} ]>".format("--" * indent, parsed_key, "IN" if parsed_key in keys_left else "NOT IN", keys_left, " ".join(result)))

                if parsed_key not in keys_left:
                    read_data = self.read(2)[1]  # Read past `:`
                    print("{}PARSE DICT (2) : `{}` <[ {} ]>".format("--" * indent, read_data, " ".join(result)))
                    if read_data == '"':
                        self.parse_string(indent=indent + 1)
                    elif read_data in ("{", "["):
                        self.extract_obj(start_char=read_data, indent=indent + 1)
                    else:
                        while True:
                            if read_data in (",", "", "}"):
                                if read_data == "}":
                                    brace_open -= 1
                                break
                            read_data = self.read(1)
                            print("{}PARSE DICT (S) : `{}`".format("--" * indent, read_data))
                else:
                    keys_left.remove(parsed_key)
                    value_map = filter_map[parsed_key]
                    if isinstance(value_map, list):
                        value_map = dict(sum(map(list, map(dict.items, value_map)), []))

                    # Read past `:`
                    self.read(1)
                    print("{}PARSE DICT (3) : `{}` <[ {} ]>".format("--" * indent, read_data, " ".join(result)))
                    parsed_value, end_char = self.parse_value(value_map=value_map, indent = indent + 1)
                    result.append('"{}":{}'.format(parsed_key, parsed_value))
                    if end_char == "}":
                        brace_open -= 1
                        result.append(end_char)
                        if brace_open <= 0:
                            return "".join(result)
                    elif not keys_left:
                        result.append("}")
                    elif keys_left:
                        result.append(",")
                    print("{}PARSE DICT (4) : <[ {} ]>".format("--" * indent, " ".join(result)))

            elif read_data == "{":
                brace_open += 1
            elif read_data == "}":
                brace_open -= 1
                # result.append("}")
                if brace_open <= 0:
                    while result[-1] == ",":
                        result.pop(-1)
                    print("{}PARSE DICT (6) : {} <[ {} ]>".format("--" * indent, brace_open, " ".join(result)))
                    return "".join(result)

    def parse_value(self, start_char = None, value_map = None, skip = False, indent=0):
        read_data = start_char
        if start_char is None:
            read_data = self.read(1)
        print("{}PARSE VALUE START : `{}`".format("--" * indent, read_data))
        if read_data == '"':
            return '"{}"'.format(self.parse_string(indent + 1)), None
        elif read_data in ("{", "["):
            if skip or value_map is True:
                return self.extract_obj(start_char=read_data, indent=indent + 1), None
            elif read_data == "{":
                return self.traverse_dict(value_map, indent=indent + 1) , None
            else:
                return self.traverse_list(value_map, indent=indent + 1), None
        else:
            if value_map is True or not skip:
                result = []
                while True:
                    if read_data in (",", '', "}", "]"):
                        if read_data in ("}", "]"):
                            result.append(read_data)
                            return "".join(result), read_data
                        print("{}PARSE VALUE : `{}` [ {} ]".format("--" * indent, read_data, " ".join(result)))
                        return "".join(result), None
                    result.append(read_data)
                    read_data = self.read(1)
            else:
                while True:
                    print("{}PARSE VALUE X: `{}`".format("--" * indent, read_data))
                    if read_data in (",", '', "}", "]"):
                        return
                    read_data = self.read(1)


if __name__ == "__main__":

    filter_map = {
        "statuses": [{
            "full_text": True,
            "id": True,
            "entities": {
                "user_mentions": [{
                    "screen_name": True
                }]},
            "retweeted_status": {
                "id": True,
                "user": {
                    "screen_name": True
                }
            },
            "user": {
                "screen_name": True
            }
        }], "errors": True
    }
    # filter_map = {"statuses": [{"wow": True, "hey": True, "cool": {"sure": True}}], "errors": True}
    # filter_map = {"a": [{"b": {"c": True}}]}

    # data = '{"ok":69,"wow":[{"a":1},{"a":2},{"a":3}],"cool":[{"yep":123}]}'
    # data = '{"_id":"5f22446b5158a04871c899fa","index":0,"guid":"df47bb04-c473-4d8c-8850-c25d6c0a3b5d","isActive":false,"balance":"$3,128.45","picture":"http://placehold.it/32x32","age":40,"eyeColor":"green","name":"Ramona Gilmore","gender":"female","company":"GEOLOGIX","email":"ramonagilmore@geologix.com","phone":"+1 (870) 498-3706","address":"487 Woodhull Street, Day, Wisconsin, 548","about":"Nisi eiusmod elit mollit mollit dolor minim duis irure. Non irure esse irure nulla aliquip est labore cupidatat. Proident adipisicing sit cupidatat est consectetur fugiat.\r\n","registered":"2017-04-06T07:57:59 +07:00","latitude":25.203187,"longitude":-82.823457,"tags":["sit","exercitation","commodo","aliquip","eiusmod","esse","esse"],"friends":[{"id":0,"name":"Esther Donovan"},{"id":1,"name":"Jackie Hester"},{"id":2,"name":"Kidd Gross"}],"greeting":"Hello, Ramona Gilmore! You have 5 unread messages.","favoriteFruit":"banana"}'
    data = ''
    with open("response.json", "r") as response:
        data += response.read()
    # print(data)
    pj = ParseJson()
    parsed_response = pj.parse_value(value_map=filter_map)[0]  + "}"
    print("-" * 15)
    print(filter_map)
    print(parsed_response)
    print(json.loads(parsed_response))



    # {"statuses":[{"wow":"ok","cool":{"sure":"bud"},"hey":{"there":"dude","take":[{"it":"easy123 3332111267^$%^@@ !@#f"}]}]}


        

            

