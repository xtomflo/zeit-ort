from ipaddress import ip_network, ip_address
import pandas as pd

# Function to extract first and last IP address from IP Range (CIDR) 
def ipnet_to_range(ip_net):
	# Get the first and last IP Network of the network and convert it to integer
	ip_range_start = int(ip_network(ip_net['network'])[0])
	ip_range_end = int(ip_network(ip_net['network'])[-1])
	
	return ip_range_start, ip_range_end

# Load the raw CSV file
ip_geoname = pd.read_csv("data/GeoLite2-City-Blocks-IPv4.csv")

# Apply the function to all IP ranges
ip_geoname[['ip_range_start','ip_range_end']] = ip_geoname.filter(like='network').apply(lambda x: ipnet_to_range(x), axis=1, result_type="expand")

# Select needed columns
ip_geoname = ip_geoname[['ip_range_start','ip_range_end','geoname_id','latitude','longitude','accuracy_radius']]

# Save results to file
ip_geoname.to_csv('data/ip_geoname.csv', index = False)
