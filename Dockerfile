FROM eclipse-temurin:17-jdk-jammy AS build
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip python3 && rm -rf /var/lib/apt/lists/*
WORKDIR /build
RUN curl --fail --location https://codeload.github.com/zb3/freej2me-web/zip/c19416e75cbc15f9a27f7e967ee81cb108761e30 -o source.zip && unzip -q source.zip && mv freej2me-web-* upstream && rm source.zip
COPY NetworkBridge.java SocketConnectionImpl.java HttpConnectionImpl.java network.js patch.py ./
RUN python3 patch.py upstream && mkdir classes && javac --release 8 -encoding UTF-8 -cp upstream/web/freej2me-web.jar -d classes NetworkBridge.java SocketConnectionImpl.java HttpConnectionImpl.java upstream/src/javax/microedition/io/Connector.java upstream/src/javax/microedition/io/InputConnection.java upstream/src/javax/microedition/io/OutputConnection.java && jar uf upstream/web/freej2me-web.jar -C classes .
RUN mkdir -p upstream/web/source && cp *.java *.js *.py upstream/web/source/ && cp upstream/src/javax/microedition/io/Connector.java upstream/src/javax/microedition/io/InputConnection.java upstream/src/javax/microedition/io/OutputConnection.java upstream/web/source/ && cp upstream/LICENSE upstream/web/source/LICENSE
FROM node:22-bookworm-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts
COPY server.mjs ./
COPY --from=build /build/upstream/web ./web
ENV NODE_ENV=production PORT=10000
USER node
EXPOSE 10000
CMD ["node","server.mjs"]
