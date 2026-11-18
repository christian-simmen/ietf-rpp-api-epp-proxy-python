from extensions.planets.rpp.mapping.member_mappers import MemberMappers

# The extensions that add members to a planet and to a satellite register their mappers here, in their `register` function.
PLANET_MEMBERS = MemberMappers()
SATELLITE_MEMBERS = MemberMappers()
