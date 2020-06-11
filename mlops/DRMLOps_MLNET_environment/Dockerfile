FROM mcr.microsoft.com/dotnet/core/sdk:3.1-buster AS build
WORKDIR /opt/code/
COPY . .
RUN dotnet build "WebServer.csproj" -c Release 
RUN dotnet publish "WebServer.csproj" -c Release

#FROM build AS final
#WORKDIR /opt/code/
# copy everything, including source code to get re-compile once new model is added
#COPY --from=build /app .
# old version without dotnet watch
#COPY --from=build /app/publish .
RUN chmod -R 777 .

ENTRYPOINT ["./start_server.sh", "&"]
