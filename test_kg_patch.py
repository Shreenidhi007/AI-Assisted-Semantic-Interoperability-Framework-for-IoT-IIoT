test_kg_code = """
        # Sensor / Device
        if obs.sensor_uri:
            sensor_ref = ENVSEN[obs.sensor_uri]
            g.add((obs_uri, SOSA.madeBySensor, sensor_ref))

            if obs.sensor_uri not in self._sensor_cache:
                g.add((sensor_ref, RDF.type, SOSA.Sensor))
                g.add((sensor_ref, RDF.type, SAREF.Sensor))
                g.add((sensor_ref, SOSA.observes, prop_uri))
                g.add((sensor_ref, RDFS.label, Literal(obs.sensor_uri)))
                self._sensor_cache.add(obs.sensor_uri)
"""

old_sensor_block = """        # Sensor / Device
        if obs.sensor_uri:
            sensor_ref = ENVSEN[obs.sensor_uri]
            g.add((obs_uri, SOSA.madeBySensor, sensor_ref))

            if obs.sensor_uri not in self._sensor_cache:
                g.add((sensor_ref, RDF.type, SOSA.Sensor))
                g.add((sensor_ref, RDF.type, SAREF.Sensor))
                g.add((sensor_ref, SOSA.observes, prop_uri))
                g.add((sensor_ref, RDFS.label, Literal(obs.sensor_uri)))
                self._sensor_cache.add(obs.sensor_uri)"""

new_sensor_block = """        # Sensor / Device
        if obs.sensor_uri:
            if obs.sensor_uri.startswith("http://") or obs.sensor_uri.startswith("https://"):
                sensor_ref = URIRef(obs.sensor_uri)
            else:
                sensor_ref = ENVSEN[obs.sensor_uri]
            g.add((obs_uri, SOSA.madeBySensor, sensor_ref))

            if str(sensor_ref) not in self._sensor_cache:
                g.add((sensor_ref, RDF.type, SOSA.Sensor))
                g.add((sensor_ref, RDF.type, SAREF.Sensor))
                g.add((sensor_ref, SOSA.observes, prop_uri))
                g.add((sensor_ref, RDFS.label, Literal(obs.sensor_label or obs.sensor_uri)))
                
                if obs.platform_uri:
                    if obs.platform_uri.startswith("http://") or obs.platform_uri.startswith("https://"):
                        platform_ref = URIRef(obs.platform_uri)
                    else:
                        platform_ref = ENVIROMAP[obs.platform_uri]
                    g.add((sensor_ref, SOSA.isHostedBy, platform_ref))
                    g.add((platform_ref, RDF.type, SOSA.Platform))
                    if obs.platform_label:
                        g.add((platform_ref, RDFS.label, Literal(obs.platform_label)))

                self._sensor_cache.add(str(sensor_ref))"""

res = test_kg_code.replace(old_sensor_block, new_sensor_block)
assert "sosa.isHostedBy" in res.lower()
print("KG patch test succeeded!")

