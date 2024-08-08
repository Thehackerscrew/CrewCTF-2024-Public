from pathlib import Path
import pickle

nodes = {}

data = bv.get_section_by_name(".data")
address = data.start

while address < data.end:
    start_address = address

    node = bv.define_user_data_var(address, bv.types["node"])
    address += len(node)

    connections = bv.define_user_data_var(address, ArrayType.create(bv.types["connection"], node.value["connection_count"]))
    address += len(connections)

    nodes[start_address] = node.value
    nodes[start_address]["instruction"] = bv.get_disassembly(nodes[start_address]["instruction"])
    nodes[start_address]["connections"] = connections.value

(Path(__file__).parent / "nodes.pickle").write_bytes(pickle.dumps(nodes))

keys = bv.get_symbol_by_raw_name("keys")
(Path(__file__).parent / "keys.data").write_bytes(bv.read(keys.address, len(bv.get_data_var_at(keys.address))))
