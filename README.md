# temporal-sdlc

# Deployment Notes
git pull (if dev)
docker compose build [env] --no-cache
docker compose up [env]

# TODO
- deploy fancy app to optiplex2
- connect deployment functionality
- add haproxy to optiplex2
-- add redirect for 3000 = prod, 3001 = dev, 3002 = preprod
-- add redirect for Temporal
- make this MCP'd
-- add to AI agent demo
-- add to Cline