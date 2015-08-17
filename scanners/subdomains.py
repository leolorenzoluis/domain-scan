import logging
from scanners import utils
import json
import os
import sys
import urllib.request
import urllib.parse
import base64
import re

##
# == subdomains ==
#
# Say whether a subdomain redirects within the domain but to another subdomain.
# Say whether a subdomain has all numbers in its leftmost subdomain.
# Say whether a subdomain has any numbers in its leftmost subdomain.
##

def scan(domain, options):
    logging.debug("[%s][subdomains]" % domain)

    # If inspection data exists, check to see if we can skip.
    inspection = utils.data_for(domain, "inspect")
    if not inspection:
        logging.debug("\tSkipping, wasn't inspected.")
        return None

    if not inspection.get("up"):
        logging.debug("\tSkipping, subdomain wasn't up during inspection.")
        return None

    # If the subdomain redirects anywhere, see if it redirects within the domain
    endpoint = inspection["endpoints"][inspection.get("canonical_protocol")]["root"]
    if endpoint.get("redirect_to"):

        sub_original = domain
        base_original = base_domain_for(domain)

        sub_redirect = urllib.parse.urlparse(endpoint["redirect_to"]).hostname
        sub_redirect = re.sub("^www.", "", sub_redirect) # discount www redirects
        base_redirect = base_domain_for(sub_redirect)
        
        redirected_external = base_original != base_redirect
        redirected_subdomain = (
            (base_original == base_redirect) and 
            (sub_original != sub_redirect)
        )
    else:
        redirected_external = False
        redirected_subdomain = False

    
    yield [
        inspection["up"],
        redirected_external,
        redirected_subdomain,
        any_numbers(subdomains_for(domain)),
        all_numbers(subdomains_for(domain)),
        any_numbers(subbest_domain_for(domain)),
        all_numbers(subbest_domain_for(domain))
    ]


headers = [
    "Live",
    "Redirects Externally",
    "Redirects To Subdomain",
    "Any Numbers",
    "All Numbers",
    "Any Numbers (Leftmost)",
    "All Numbers (Leftmost)"
]

# does a number appear anywhere in this thing
def any_numbers(string):
    return (re.search(r'\d', string) is not None)

# is it all numbers (and dots)
def all_numbers(string):
    return (re.search(r'^[\d\.]+$', string) is not None)

# return base domain for a subdomain
def base_domain_for(subdomain):
    return str.join(".", subdomain.split(".")[-2:])

# return everything to the left of the base domain
def subdomains_for(subdomain):
    return str.join(".", subdomain.split(".")[:-2])

# return the leftmost subdomain
def subbest_domain_for(subdomain):
    return subdomain.split(".")[0]
