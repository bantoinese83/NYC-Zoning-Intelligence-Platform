# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy package files
COPY package*.json ./

# Change ownership of the working directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Install dependencies
RUN npm ci

# Copy source code
COPY --chown=nextjs:nodejs . .

# Create .next directory and set permissions (do this as root before switching user)
USER root
RUN mkdir -p .next && chown -R nextjs:nodejs .next
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV NODE_ENV=development

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the development server
CMD ["npm", "run", "dev"]