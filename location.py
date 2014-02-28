from sessions import *
from protocol import *

def distanceOnUnitSphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * EARTH_RADIUS

def getNearbyClients(clients, curClient):
    for client in clients:
        if client == curClient:
            continue
        c = client.user
        u = curClient.user
        if (c.latitude != UNASSIGNED_DEGREE and c.longitude != UNASSIGNED_DEGREE and u.latitude != UNASSIGNED_DEGREE and u.longitude != UNASSIGNED_DEGREE):
            if (distanceOnUnitSphere(c.latitude, c.longitude, u.latitude, u.longitude) < 0.5):
                yield client

def processLoc(chatProtocol, content):
    if chatProtocol.user.userId == 0:
        chatProtocol.message(CMD_REJOIN, '')
        return
    strArray = content.split('|')
    if len(strArray) < 2:
        return
    try:
        latitude = float(strArray[0])
        longitude = float(strArray[1])
        chatProtocol.user.latitude = latitude
        chatProtocol.user.longitude = longitude
    except:
        print 'error converting coorindates'
registerProcessor(CMD_LOC, processLoc)
