FROM emqx/emqx:5.7.2

# Copia solo el archivo de reglas al directorio de configuraciones adicionales.
# EMQX cargará automáticamente cualquier archivo .conf de esta carpeta.
COPY emqx_rule_config.conf /opt/emqx/etc/configs/my_rules.conf