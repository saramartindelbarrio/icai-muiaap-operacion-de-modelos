# Explainer — Del lienzo a un bundle ejecutable

El starter conserva dos decisiones de la semana 3:

- WineQualityRequest valida cada muestra;
- preprocess_wine_request() construye el vector con once nombres y un orden
  fijo.

La pareja implementa solo la nueva frontera:

~~~text
ArtifactManifest -> save_model_bundle/load_model_bundle
                         ↓
                   infer_wine_quality
                         ↓
                       CLI CSV
~~~

La salida debe validarse igual que la entrada. El éxito de joblib.load() no
demuestra que el artefacto sea compatible: primero se valida el manifiesto y
después se comprueba la interfaz del estimador.
