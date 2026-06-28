# AZL Physical Serverless Node
FROM oven/bun:1-alpine

WORKDIR /azl
COPY worker.js ./server.js

# Add local batch lookup later: COPY batches/ ./batches/

EXPOSE 8080

# "Serverless" behavior: bun starts in <50ms, idles at 5MB RAM
CMD ["bun", "run", "server.js"]

# Health check = CI for your box
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -qO- http://localhost:8080/azl/v1/health || exit 1
