"""Módulo para calcular distancias en carretera usando OSRM."""

import requests
import time
from math import radians, cos, sin, asin, sqrt


class DistanceCalculator:
    """Clase para calcular distancias entre puntos usando diferentes métodos."""
    
    # OSRM público: http://router.project-osrm.org (para pruebas, limitado)
    OSRM_URL = "http://router.project-osrm.org/route/v1/driving"
    
    # Alternativa más rápida: usar haversine como fallback
    
    @staticmethod
    def haversine(lon1, lat1, lon2, lat2):
        """
        Calcula la distancia en línea recta entre dos puntos usando Haversine.
        Retorna la distancia en km.
        
        Nota: Esta es una aproximación. Para distancias en carretera, usar OSRM.
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radio de la Tierra en km
        return c * r
    
    @staticmethod
    def get_distance_osrm(lat1, lon1, lat2, lon2):
        """
        Obtiene la distancia en carretera entre dos puntos usando OSRM.
        Retorna la distancia en km.
        
        Args:
            lat1, lon1: Coordenadas del punto origen
            lat2, lon2: Coordenadas del punto destino
            
        Returns:
            Distancia en km o None si hay error
        """
        try:
            # OSRM espera coordenadas en formato (lon,lat)
            url = f"{DistanceCalculator.OSRM_URL}/{lon1},{lat1};{lon2},{lat2}"
            
            params = {
                'overview': 'false',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == 'Ok' and len(data['routes']) > 0:
                # Convertir de metros a km
                distance_meters = data['routes'][0]['distance']
                return distance_meters / 1000
            else:
                return None
                
        except Exception as e:
            print(f"Error obteniendo distancia OSRM: {e}")
            return None
    
    @staticmethod
    def calculate_distance_matrix(df_locations, use_osrm=True, verbose=True):
        """
        Calcula la matriz de distancias entre todos los puntos.
        
        Args:
            df_locations: DataFrame con columnas 'Latitud' y 'Longitud'
            use_osrm: Si True, usa OSRM. Si False, usa Haversine
            verbose: Si True, muestra progreso
            
        Returns:
            Matriz 2D con las distancias (lista de listas)
        """
        n = len(df_locations)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        total_pairs = (n * n)
        processed = 0
        
        for i in range(n):
            lat1 = df_locations.iloc[i]['Latitud']
            lon1 = df_locations.iloc[i]['Longitud']
            
            for j in range(n):
                if i == j:
                    matrix[i][j] = 0.0
                else:
                    lat2 = df_locations.iloc[j]['Latitud']
                    lon2 = df_locations.iloc[j]['Longitud']
                    
                    if use_osrm:
                        # Intentar OSRM primero
                        distance = DistanceCalculator.get_distance_osrm(lat1, lon1, lat2, lon2)
                        
                        # Si falla, usar Haversine
                        if distance is None:
                            distance = DistanceCalculator.haversine(lon1, lat1, lon2, lat2)
                    else:
                        distance = DistanceCalculator.haversine(lon1, lat1, lon2, lat2)
                    
                    matrix[i][j] = round(distance, 2)
                    
                    # Añadir pequeña pausa para no sobrecargar OSRM
                    if i != j and use_osrm:
                        time.sleep(0.1)
                
                processed += 1
                if verbose and processed % 10 == 0:
                    print(f"Progreso: {processed}/{total_pairs} pares calculados")
        
        if verbose:
            print(f"Cálculo completado: {processed}/{total_pairs} pares")
        
        return matrix
