### Flujo de Trabajo con Scrum

Para el desarrollo, aplicamos prácticas de desarrollo ágil con Scrum y gestionamos el flujo de trabajo con Git Flow. Esto permite mejorar la colaboración en equipo, organizar las tareas de manera eficiente y mantener un control claro sobre las versiones.

#### Metodología Scrum

1. **Definir el Product Backlog:** Lista de requisitos y funcionalidades de la landing page.
2. **Planificación del Sprint:** Seleccionar tareas prioritarias para el Sprint actual (1-4 semanas).
3. **Daily Scrum:** Reunión diaria para revisar avances y obstáculos.
4. **Desarrollo incremental:** Construir y probar funcionalidades en cada Sprint.
5. **Revisión del Sprint:** Mostrar el avance al Product Owner y recibir feedback.
6. **Retrospectiva:** Analizar el proceso y proponer mejoras para el siguiente Sprint.

#### Convenciones de ramas y commit
 
**Ramas principales:**
- `main`: contiene la versión estable y lista para producción.
- `develop`: integra las nuevas funcionalidades antes de pasar a producción.

**Ramas de soporte:**
- `feature/nombre-funcionalidad`: para nuevas características.
- `bugfix/nombre-arreglo`: para corrección de errores.
- `hotfix/nombre-arreglo`: para arreglos urgentes en producción.
- `release/nombre-version`: para preparar una nueva versión.
- `docs/nombre-documento`: para cambios en la documentación.

**Convención de commits:**
- Utilizar mensajes breves y descriptivos en infinitivo, siguiendo el formato `tipo: descripción`.
- Tipos de commit más comunes:
    - `feat`: nueva funcionalidad o feature
    - `fix`: corrección de errores
    - `docs`: cambios en la documentación
    - `style`: cambios de formato (espacios, indentación, comas, etc.) que no afectan el código
    - `refactor`: refactorización del código que no corrige errores ni agrega funcionalidades
    - `test`: agregar o modificar pruebas
    - `chore`: tareas de mantenimiento o cambios menores que no afectan la funcionalidad
- Ejemplos:
    - `feat: agregar sección de contacto`
    - `fix: corregir error en formulario`
    - `docs: actualizar instrucciones de instalación`
    - `style: corregir indentación en archivo main.js`
    - `refactor: simplificar función de validación`
    - `test: agregar pruebas para el componente Header`
    - `chore: actualizar dependencias del proyecto y modificar los requirements`