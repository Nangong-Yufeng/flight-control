import folium

def test001():
    print('000001')

def createMap(map_lat, map_lon):
    Map = folium.Map(location=[map_lat, map_lon],
                    max_zoom=19, 
                    zoom_start=18, 
                    crs="EPSG3857", 
                    control_scale=True,
                    #  tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
                    tiles = 'OpenStreetMap',  # 使用OpenStreetMap
                    attr='default')
    folium.CircleMarker(
        location=[map_lat, map_lon],
        radius=1,
        popup='popup',
        color='#DC143C',      # 圈的颜色
        fill=True,
        fill_color='#6495E'  # 填充颜色
    ).add_to(Map)
    Map.add_child(folium.LatLngPopup())                     # 显示鼠标点击点经纬度
    Map.add_child(folium.ClickForMarker(popup='Waypoint'))  # 将鼠标点击点添加到地图上

    return Map

def mark3Points(Map, tar_pos):
    folium.Marker(
        location=[tar_pos[0][0], tar_pos[0][1]],
        popup="target1",
        icon=folium.Icon(icon="battery-0", prefix='fa'),
    ).add_to(Map)
    folium.Marker(
        location=[tar_pos[1][0], tar_pos[1][1]],
        popup="target2",
        icon=folium.Icon(icon="battery-1", prefix='fa'),
    ).add_to(Map)
    folium.Marker(
        location=[tar_pos[2][0], tar_pos[2][1]],
        popup="target3",
        icon=folium.Icon(icon="battery-2", prefix='fa'),
    ).add_to(Map)
