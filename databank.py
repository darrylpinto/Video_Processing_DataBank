import pickle
import socket


class databank:
    # Output is the shared buffer, table is the table of pointers

    __slots__ = "output", "flow_table", "id", "operator", "input"

    def __init__(self, id, operator=None):
        self.output = []
        self.input = []
        self.flow_table = {}
        self.id = id
        self.operator = operator

    def set_operator(self, operator):
        self.operator = operator

    def add_edge(self, nbr_databank):
        self.flow_table[nbr_databank.id] = nbr_databank

    def use_operator(self):
        self.output = self.operator(self.input)

    def server(self):

        WINDOW_SIZE = 4096
        PORT = 9000 + self.id

        # Open the server socket and bind it and listening for request
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSock.bind(('', PORT))
        serverSock.listen(10)

        source_data_dict = {}

        while True:
            print("**Waiting for new connection")

            soc, addr = serverSock.accept()

            # Receive the ID of the user
            id = pickle.loads(soc.recv(WINDOW_SIZE))

            if id not in source_data_dict:
                source_data_dict[id] = []

            try:

                content = soc.recv(WINDOW_SIZE)
                by = bytearray()

                while content:
                    by.extend(content)
                    content = soc.recv(WINDOW_SIZE)

                    if len(content) == 0:
                        img_lst = pickle.loads(by)
                        source_data_dict[id].extend(img_lst)
                        break

            except EOFError:
                print("EOFError")

            print(len(source_data_dict[id]))
            print("\n")

            # Close file and socket
            soc.close()

    def client(self, host, np_obj, host_id):

        WINDOW_SIZE = 4096
        port = 9000
        HOST = host
        PORT = port + host_id

        # Define socket and connect to server
        # soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # soc.connect((HOST, PORT))

        # Get the length of your output buffer
        IMAGE_BURST = len(self.output)
        buffer_list = []

        for i in range(IMAGE_BURST + 1):

            if i != IMAGE_BURST:
                buffer_list.append(self.output[i])

            if (i + 1) % IMAGE_BURST == 0:  # or i == len(img_list):

                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.connect((HOST, PORT))

                # Send ID
                soc.send(pickle.dumps(id))

                # Send the Buffer
                np_serial = pickle.dumps(buffer_list)
                start = 0
                end = WINDOW_SIZE

                # Read bytes from file and send until the end of file
                content = np_serial[start:end]

                while content:
                    soc.send(content)
                    start += WINDOW_SIZE
                    end += WINDOW_SIZE
                    content = np_serial[start:end]
                buffer_list = []

                print("*Buffer Sent")

                # Close socket
                soc.close()
