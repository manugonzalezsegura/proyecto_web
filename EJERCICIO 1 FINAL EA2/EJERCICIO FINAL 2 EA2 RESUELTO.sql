VARIABLE b_fecha VARCHAR2(6);
EXEC :b_fecha := '202106';
VARIABLE b_limite_asig NUMBER;
EXEC :b_limite_asig := 250000;
DECLARE
   /* Cursor que recupera datos de las profesiones */
   CURSOR cur_profesion IS 
   SELECT cod_profesion, nombre_profesion
   FROM profesion
   ORDER BY nombre_profesion;

   /* Cursor que recupera datos de los profesionales de una profesión determinada
    que hayan realizado asesorías en el mes que se está procesando */
   CURSOR cur_profesional (p_cod_profesion NUMBER) IS
   SELECT TO_CHAR(p.numrun_prof,'99G999G999') || '-' || p.dvrun_prof RUN, P.nombre || ' ' || P.appaterno nombre, 
          p.cod_profesion, p.cod_tpcontrato, 
          p.cod_comuna, p.sueldo,
          COUNT(a.numrun_prof) cantidad_asesorias, SUM(a.honorario) monto_asesorias
   FROM profesional P JOIN asesoria a
     ON p.numrun_prof=a.numrun_prof
   WHERE to_char(a.inicio_asesoria, 'YYYYMM') = :b_fecha
   AND p.cod_profesion = p_cod_profesion
   --and p.numrun_prof=6694138
   GROUP BY p.numrun_prof,p.dvrun_prof, p.nombre,p.appaterno,p.cod_profesion,p.cod_tpcontrato,p.cod_comuna,p.sueldo
  ORDER BY p.appaterno, p.nombre;

-- Defición variables escalares 
v_msg VARCHAR2(300);
v_msgusr VARCHAR2(300);
v_asig_mov_extra NUMBER(8);
v_porc_asig NUMBER(5,3);
v_asig_prof NUMBER(8);
v_porc_tpcont NUMBER(5,3);
v_asig_tpcont NUMBER(8);
v_asignaciones NUMBER(8) := 0;
-- variables escalares acumuladoras
v_tot_asesorias NUMBER(8);
v_tot_honorarios NUMBER(8);
v_tot_asig_mov NUMBER(8);
v_tot_asig_tpcont NUMBER(8);
v_tot_asig_prof NUMBER(8);
v_tot_asignaciones NUMBER(8);   
-- Defición Varray para almacenar los porcentajes de asignación movilización extra
TYPE t_varray_porc_mov IS VARRAY(5) OF NUMBER;
varray_porc_mov t_varray_porc_mov;
-- Definición Excepción del Usuario para controlar el valor tope de asignaciones
asignacion_limite EXCEPTION;

BEGIN
   -- TRUNCA TABLAS
   EXECUTE IMMEDIATE 'TRUNCATE TABLE ERRORES_PROCESO';
   EXECUTE IMMEDIATE 'TRUNCATE TABLE DETALLE_ASIGNACION_MES';
   EXECUTE IMMEDIATE 'TRUNCATE TABLE RESUMEN_MES_PROFESION';
   EXECUTE IMMEDIATE 'DROP SEQUENCE SQ_ERROR';
   EXECUTE IMMEDIATE 'CREATE SEQUENCE SQ_ERROR';
   varray_porc_mov:= t_varray_porc_mov(0.02,0.04,0.05,0.07,0.09);
   -- CURSOR QUE LEE LAS PROFESIONES
   FOR reg_profesion IN cur_profesion LOOP 
       -- Se inicializan las variables totalizadoras en cero  
        v_tot_asesorias:=0;
        v_tot_honorarios:=0;
        v_tot_asig_mov:=0;
        v_tot_asig_tpcont:=0;
        v_tot_asig_prof:=0;
        v_tot_asignaciones:=0;        
        /* CURSOR QUE POR CADA PROFESION LEIDA DEL PRIMER CURSOR OBTIENE A LOS EMPLEADOS DE ESA PROFESION
        EN EL SEGUNDO CURSOR */
       FOR reg_profesional IN cur_profesional (reg_profesion.cod_profesion) LOOP
          dbms_output.put_line(reg_profesional.cod_comuna);
          dbms_output.put_line(reg_profesional.monto_asesorias);
           -- Calcula asignación movilización extra
           v_asig_mov_extra:=0;
           IF reg_profesional.cod_comuna=82 AND reg_profesional.monto_asesorias < 3500000 THEN 
               dbms_output.put_line('cumplo');
              v_asig_mov_extra:=ROUND(reg_profesional.monto_asesorias*varray_porc_mov(1));
           ELSIF reg_profesional.cod_comuna=83 THEN
                 v_asig_mov_extra:=ROUND(reg_profesional.monto_asesorias*varray_porc_mov(2));
           ELSIF reg_profesional.cod_comuna=85 AND reg_profesional.monto_asesorias < 4000000 THEN
                 v_asig_mov_extra:=ROUND(reg_profesional.monto_asesorias*varray_porc_mov(3));                   
           ELSIF reg_profesional.cod_comuna=86 AND reg_profesional.monto_asesorias < 8000000 THEN
                 v_asig_mov_extra:=ROUND(reg_profesional.monto_asesorias*varray_porc_mov(4));   
           ELSIF reg_profesional.cod_comuna=89 AND reg_profesional.monto_asesorias < 6800000 THEN
                 v_asig_mov_extra:=ROUND(reg_profesional.monto_asesorias*varray_porc_mov(5)); 
           END IF;
           
           -- Calcula asignación especial profesional
           BEGIN
               SELECT asignacion / 100
               INTO v_porc_asig
               FROM porcentaje_profesion
               WHERE cod_profesion=reg_profesional.cod_profesion;        
           EXCEPTION    
             WHEN OTHERS THEN
                v_msg := SQLERRM;
                v_porc_asig := 0; 
                v_msgusr := 'Error al obtener porcentaje de asignacion para el empleado con run: ' || reg_profesional.run;
                INSERT INTO errores_proceso
                VALUES (sq_error.NEXTVAL, v_msg, v_msgusr);
           END;
           v_asig_prof:= ROUND(reg_profesional.monto_asesorias * v_porc_asig);

          -- Calculo asignación por tipo de contrato
          SELECT incentivo/100
          into v_porc_tpcont  
          from tipo_contrato
          where cod_tpcontrato = reg_profesional.cod_tpcontrato;
          v_asig_tpcont := ROUND(reg_profesional.monto_asesorias * v_porc_tpcont);

          -- calculamos el total de las asignaciones
          v_asignaciones:=v_asig_mov_extra+v_asig_prof+v_asig_tpcont;

          /* Control Excepción Predefinina para controlar que el monto de asignaciones no puede ser 
           mayor a $250.000 */
          BEGIN
              IF v_asignaciones > :b_limite_asig THEN
                  RAISE asignacion_limite;  
              END IF;
          EXCEPTION
              WHEN asignacion_limite THEN
                 v_msg := 'Error, el profesional con run: ' || reg_profesional.run || ' supera el monto límite de asignaciones';
                    INSERT INTO errores_proceso
                    VALUES (sq_error.NEXTVAL, v_msg,
                           'Se reemplazó el monto total de las asignaciones calculadas de ' ||
                           v_asignaciones || ' por el monto límite de ' ||
                           :b_limite_asig);
                 v_asignaciones := :b_limite_asig;
          END;

          -- INSERCION EN LA TABLA DE DETALLE
          INSERT INTO detalle_asignacion_mes
          VALUES (SUBSTR(:b_fecha,-2),SUBSTR(:b_fecha,1,4),reg_profesional.RUN,reg_profesional.nombre,
                 reg_profesion.nombre_profesion,
                  reg_profesional.cantidad_asesorias,reg_profesional.monto_asesorias,
                  v_asig_mov_extra,v_asig_tpcont,v_asig_prof,v_asignaciones);
                     
         /* SE REALIZA LA SUMATORIA A LAS VARIABLES TOTALIZADORAS QUE SE REQUIEREN PARA INSERTAR
            EN LA TABLA RESUMEN */
          v_tot_asesorias := v_tot_asesorias + reg_profesional.cantidad_asesorias;
          v_tot_honorarios := v_tot_honorarios + reg_profesional.monto_asesorias;
          v_tot_asig_mov := v_tot_asig_mov + v_asig_mov_extra;
          v_tot_asig_tpcont := v_tot_asig_tpcont + v_asig_tpcont;
          v_tot_asig_prof := v_tot_asig_prof + v_asig_prof;
          v_tot_asignaciones:= v_tot_asignaciones + v_asignaciones;
          
       END LOOP;
       
       -- INSERCION EN LA TABLA DE RESUMEN
       INSERT INTO resumen_mes_profesion
       VALUES (:b_fecha, reg_profesion.nombre_profesion,v_tot_asesorias,v_tot_honorarios,
              v_tot_asig_mov, v_tot_asig_tpcont,v_tot_asig_prof,v_tot_asignaciones); 
   END LOOP;
   COMMIT;
END;  
