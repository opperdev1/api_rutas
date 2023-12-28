from __future__ import print_function
import pandas as pd
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import json
import urllib
import urllib.request,urllib.parse, urllib.error
import numpy as np



def create_data_model(df,vehiculos=2):
    #creamos datos
    data={}
    data['name']=df['id'].values
    data['latitud']=df['Latitud'].values
    data['longitud']=df['Longitud'].values
    data['num_vehicles'] = vehiculos
    data['depot'] = 0
    return data

def enviar_request(latitudes,longitudes):
    def construir_direccion_str(latitudes,longitudes):
        coordenadas_str = ''
        for i in range(len(latitudes) - 1):
            coordenadas_str += f'{longitudes[i]},{latitudes[i]}' + ';'
        coordenadas_str +=f'{longitudes[-1]},{latitudes[-1]}'
        return coordenadas_str
    request = 'http://router.project-osrm.org/table/v1/driving/'
    coordenadas_str=construir_direccion_str(latitudes,longitudes)
    request += coordenadas_str + '?annotations=distance'
    #print(request)
    jsonResult = urllib.request.urlopen(request).read()
    response = json.loads(jsonResult)
    return response
#response=enviar_request(data['latitud'],data['longitud'])

def construir_distance_matrix(response):
  distance_matrix = [row for row in response['distances']]

  distance_matrix = np.around(distance_matrix,0)
  distance_matrix = distance_matrix.astype(int)

  distance_matrix= distance_matrix.tolist()
 
  return distance_matrix


def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['distance_matrix'][from_node][to_node]


def get_route(data,solution, routing, manager):
    # Get vehicle routes and store them in a two dimensional array whose
  # i,j entry is the jth location visited by vehicle i along its route.
    routes = []
    for route_nbr in range(data['num_vehicles']):
        index = routing.Start(route_nbr)
        route = [manager.IndexToNode(index)]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
        routes.append(route)
    return routes


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    solutionlist=[]
    max_route_distance = 0
    
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        solutionlist.append(plan_output)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        #print(plan_output)
        solutionlist.append(plan_output)
        

        max_route_distance = max(route_distance, max_route_distance)
    
    m='Maximum of the route distances: {}m'.format(max_route_distance)
    #print(m)
    solutionlist.append(m)

    return solutionlist


def mainRutas(obj=None):
     

    data2=obj;
    #data2=None;
    if data2 is None:
        with open('data2.json', 'r') as f:
            data = json.load(f)
        f.close()
    else:
        data = data2   


    print(data)
    datos=[[0,data['nombre'],data['lat'],data['lon']]]
    vehiculos = data['vehiculos']

    for i in range(len(data['pedidos'])):
        datos.append([i+1,data["pedidos"][i]['id_pedidos'],data["pedidos"][i]['lat'],data["pedidos"][i]['lon']])
    datos =  pd.DataFrame(datos,columns=['n','id','Latitud','Longitud'] )
    data = create_data_model(datos,vehiculos)
    response=enviar_request(data['latitud'],data['longitud'])        
        
        
    data['distance_matrix']=construir_distance_matrix(response)
    

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    #print(data)
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    #print(data)
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        25000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.seconds = 60

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    
    

    # Print solution on console.
    if solution:
        salida=print_solution(data, manager, routing, solution)
        routes = get_route(data,solution, routing, manager)
        #print(routes)
        rutas_dic ={}

        df1=pd.DataFrame(columns=['vehicle','n','id','Latitud','Longitud'])
    
        k = 0
        for j in range(len(routes)):

            lista=routes[j]
            rutas_dic[j] = routes[j][1:-1]
            

            
        #texto=['Route for vehicle 0:\n']                   
                        
            
            for i,l in enumerate(lista):
                df1.loc[k]=[j,i,datos['id'][l],datos['Latitud'][l],datos['Longitud'][l]]
                k+=1
        #print(df1)
        lista_rutas = [rutas_dic[i] for i in range(len(rutas_dic)) ]
        result_rutas2 = {}
        for i in range(len(lista_rutas)):
            lista_aux = lista_rutas[i]
            seleccion = pd.DataFrame()
            rutas = []
            for j in range(len(lista_aux)):
                seleccion = datos[datos['n'] == lista_aux[j]]['id'].values[0]
                #print (seleccion)
                rutas.append(seleccion)
            result_rutas2[i] = rutas
#        print(result_rutas2)
        
        
        
    else:
        print('No solution found !')
        result_rutas2 = {}
    return result_rutas2

#if __name__ == '__main__':
#    mainRutas()