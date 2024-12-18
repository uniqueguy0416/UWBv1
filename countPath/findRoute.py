import json


class Graph:
    def __init__(self, size):
        self.adj_matrix = [[0] * size for _ in range(size)]
        self.size = size
        self.vertex_data = [[]] * size

    def add_edge(self, u, v, weight):
        if 0 <= u < self.size and 0 <= v < self.size:
            self.adj_matrix[u][v] = weight
            self.adj_matrix[v][u] = weight  # For undirected graph

    def add_vertex_data(self, vertex, data):
        if 0 <= vertex < self.size:
            self.vertex_data[vertex] = data

    def dijkstra(self, start_vertex_data):
        start_vertex = self.vertex_data.index(start_vertex_data)
        distances = [float('inf')] * self.size
        distances[start_vertex] = 0
        visited = [False] * self.size

        tempRoute = []
        nodeList = [i for i in range(self.size)]
        for _ in range(self.size):
            min_distance = float('inf')
            u = None
            for i in range(self.size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i
            tempRoute.append((nodeList[u], u))
            if u is None:
                break

            visited[u] = True

            for v in range(self.size):
                if self.adj_matrix[u][v] != 0 and not visited[v]:
                    alt = distances[u] + self.adj_matrix[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
                        nodeList[v] = u

        target = 9
        route = [target]
        for i in range(len(tempRoute)-1, -1, -1):
            if tempRoute[i][1] == target:
                target = tempRoute[i][0]
                route.append(target)
            if target == 0:
                break
        print(route)

        return route

# check if two lines intersect


def checkIntersection(A, B, C, D):
    # Ax + By = C
    a1 = B[1] - A[1]
    b1 = A[0] - B[0]
    c1 = a1 * A[0] + b1 * A[1]

    a2 = D[1] - C[1]
    b2 = C[0] - D[0]
    c2 = a2 * C[0] + b2 * C[1]

    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        return None  # lines are parallel

    x = (b2 * c1 - b1 * c2) / determinant
    y = (a1 * c2 - a2 * c1) / determinant
    if (min(A[0], B[0]) <= x <= max(A[0], B[0]) and min(A[1], B[1]) <= y <= max(A[1], B[1]) and min(C[0], D[0]) <= x <= max(C[0], D[0]) and min(C[1], D[1]) <= y <= max(C[1], D[1])):
        return True
    return False

# add edge between st and dst if there is no intersection


def addEdge(st, dst, data):
    inter = False
    for box in data['box']:
        if (inter):  # if intersection found
            break
        for k in range(4):

            if (checkIntersection(graph.vertex_data[st], graph.vertex_data[dst], box['edge'][k], box['edge'][(k+1) % 4])):
                graph.add_edge(st, dst, 0)
                inter = True
                break

    if (not inter):
        len = ((graph.vertex_data[st][0] - graph.vertex_data[dst][0])**2 +
               (graph.vertex_data[st][1] - graph.vertex_data[dst][1])**2)**0.5
        graph.add_edge(st, dst, len)


def findRoute(st=[], dest=[]):
    print(dest, type(dest), "dest")
    if dest == []:
        return []

    # st = [121.5444944, 25.01802]

    global graph
    graph = Graph(10)

    # load information from json file
    with open('points.json', 'r') as file:
        data = json.load(file)

    # add vertex data
    graph.add_vertex_data(0, st)
    graph.add_vertex_data(9, dest)
    for node in data['cross']:
        graph.add_vertex_data(node['id'], node['pos'])

    # add edges (original cross)
    for i in range(1, 9):
        for k in range(i + 1, 9):
            if k-i == 1 or k-i == 4:
                if k != 5 or i != 4:
                    print(i, k)
                    len = ((graph.vertex_data[i][0] - graph.vertex_data[k][0])**2 +
                           (graph.vertex_data[i][1] - graph.vertex_data[k][1])**2)**0.5
                    graph.add_edge(i, k, len)
            else:
                graph.add_edge(i, k, 0)
    print(graph.adj_matrix)
    # add edges (st and dest)
    addEdge(0, 9, data)
    for i in range(1, 9):
        addEdge(0, i, data)
        addEdge(9, i, data)
    route = graph.dijkstra(st)
    finalRoute = []
    for i in route:
        finalRoute.append(graph.vertex_data[i])

    print(finalRoute)
    return finalRoute


if __name__ == "__main__":
    findRoute()
