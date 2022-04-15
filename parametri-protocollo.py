#from this import d
import pandas as pd
import math
pd.options.mode.chained_assignment = None

""" 
--------------------------------------------------------
ANALISI GAZE, FIXATIONS AND PUPILS CSV ON SURFACE FINALE
--------------------------------------------------------

"""

# Lettura dei file csv di sguardo, fissazione e pupille
df_gaze = pd.read_csv('gaze_positions_on_surface_Infotainment.csv', usecols=['gaze_timestamp','x_norm','y_norm','on_surf', 'confidence'])
df_fix = pd.read_csv('fixations_on_surface_Infotainment.csv', usecols=['fixation_id','world_timestamp','duration','norm_pos_x','norm_pos_y','on_surf'])
df_pupil = pd.read_csv('pupil_positions.csv', usecols=['pupil_timestamp','eye_id','confidence','norm_pos_x','norm_pos_y','diameter', 'diameter_3d'])

# Tempo totale della registrazione
t0 = df_gaze['gaze_timestamp'].values[0]
t1 = df_gaze['gaze_timestamp'].values[-1]
tempo_totale = t1 - t0

print("TOTAL : ",t0, t1, tempo_totale)
print("")

tempo_totale_registrazione = 0
tempo_on_surf_registrazione = 0
# Ciclo for ripetuto per i 5 task della registrazione
# start_time e stop_time sono valori inseriti manualmente 
# Corrispondono al tempo di inizio e fine di ogni task  
for i in range (5):
    if i == 0:
        start_time_task2 = t0 + 35.724
        stop_time_task2 = t0 + 66.531
    if i == 1:
        start_time_task2 = t0 + 72.960
        stop_time_task2 = t0 + 76.230
    if i == 2:
       start_time_task2 = t0 + 81.014
       stop_time_task2 = t0 + 100.531
    if i == 3:
        start_time_task2 = t0 + 106.524
        stop_time_task2 = t0 + 109.231
    if i == 4:
        start_time_task2 = t0 + 112.261
        stop_time_task2 = t0 + 149.231

    print("--------------------------TASK ",i + 1,"--------------------------")
    # Filtro dati oculari per task in base ai tempi start_time e stop_time rilevati manualmente
    filter_on_task2 = (df_gaze['gaze_timestamp'] >= start_time_task2) & (df_gaze['gaze_timestamp'] <= stop_time_task2)

    df_task = df_gaze[filter_on_task2]

    # Filtro dati oculari per confidenza, vengono considerati solo valori >0.6 
    filter_on_confidence_gaze = (df_task['confidence'] >= 0.6)
    df_task2 = df_task[filter_on_confidence_gaze]

    # Filtro dati oculari sulla superficie, on_surf == true quando lo sguardo è sull'infotainment
    filter_on_surf_gaze_t2 = (df_task2['on_surf']) 
    df_on_surf_gaze_t2 = df_task2[filter_on_surf_gaze_t2]

    # Da T/F a 1/0
    df_task2['binary_on_surf'] = df_task2['on_surf'] * 1

    # Differenza e fill NaN in 0, ottengo il df con la colonna 'binary_on_surf' che contiene le transizioni 
    df_task2['binary_on_surf'] = df_task2['binary_on_surf'].diff()
    df_task2['binary_on_surf'] = df_task2['binary_on_surf'].fillna(0)

    # Filtro tutte le transizioni: 1 da F->V, -1 da V->F
    filter_transitions2 = ((df_task2['binary_on_surf'] == 1) | (df_task2['binary_on_surf'] == -1))
    df_task2 = df_task2[filter_transitions2]

    # Differenza per calcolare il tempo tra le transizioni: Aggiungo colonna 'difference_timestamp'
    # che calcola il tempo tra una transizione e l'altra
    df_task2['difference_timestamp'] = df_task2['gaze_timestamp'].diff()
    df_task2['difference_timestamp'] = df_task2['difference_timestamp'] #.fillna(0)

    # Filtro per transizioni pos e neg: suddivido il df per tipologia di transizione
    # [pos_transition 1 da F->V, neg_transition -1 da V->F]
    # time_transition_TRUE è il df contenente in difference_timestamp le transizioni da V->F, quindi il tempo on surf
    # time_transition_FALSE è il df contenente difference_timestamp le transizioni da F->V, quindi il tempo off surf
    filter_N_trans2 = (df_task2['binary_on_surf'] == -1.0)
    df_time_transition_TRUE2 = df_task2[filter_N_trans2]

    filter_P_trans2 = (df_task2['binary_on_surf'] == 1.0)
    df_time_transition_FALSE2 = df_task2[filter_P_trans2]

    
    # Tempi iniziali e finali prima di transizioni. Calcolo il tempo tra l'inizio del task e la prima transizione
    # e il tempo tra l'ultima transizione e la fine del task
    t_iniziale_scarto_t2 = df_task2['gaze_timestamp'].values[0] - start_time_task2
    t_finale_scarto_t2 = stop_time_task2 - df_task2['gaze_timestamp'].values[-1] 

    t_iniziale_scarto_t2 = 0.5
    t_finale_scarto_t2 = 0.5
    # Calcolo la somma di difference_timestamp per ogni df_transition, aggiungendo i tempi "scarto"
    total_time_on_surf2 = df_time_transition_TRUE2['difference_timestamp'].sum()
    total_time_off_surf2 = df_time_transition_FALSE2['difference_timestamp'].sum() + t_iniziale_scarto_t2 + t_finale_scarto_t2 
    total_time_t2 = total_time_on_surf2 + total_time_off_surf2

    # Conto il numero di volte in cui avviene una transizione F->V 
    number_on_surf_glances2 = df_time_transition_FALSE2['on_surf'].count()

    # Calcolo la percentuale di tempo di sguardo su superficie
    percentage_on_surf = total_time_on_surf2 / total_time_t2 * 100

    tempo_totale_registrazione += total_time_t2
    tempo_on_surf_registrazione += total_time_on_surf2

    print('TOTAL TASK TIME:\t', round(total_time_t2, 3), "s")
    print('TOTAL TIME ON SURF:\t', round(total_time_on_surf2, 3), "s") 
    print('TOTAL TIME OFF SURF:\t', round(total_time_off_surf2, 3), "s") 
    print('MAX t ON surf CONSEC:\t', round(df_time_transition_TRUE2['difference_timestamp'].max(),3)) 
    print('NUMBER ON SURF TRANS:\t', number_on_surf_glances2)

    
    #print('MIN t ON surf CONSEC:\t', round(df_time_transition_TRUE2['difference_timestamp'].min(),3))
    
#    if (number_on_surf_glances2 == 1):
#        if (t_iniziale_scarto_t2 < t_finale_scarto_t2):
#            print('MAX t OFF surf CONSEC:\t', round(t_finale_scarto_t2,3))
#            #print('MIN t OFF surf CONSEC:\t', round(t_iniziale_scarto_t2,3))
#        else:
#            print('MAX t OFF surf CONSEC:\t', round(t_iniziale_scarto_t2,3))
#            print('MIN t OFF surf CONSEC:\t', round(t_finale_scarto_t2,3)) 
#    else:      
#        print('MAX t OFF surf CONSEC:\t', round(df_time_transition_FALSE2['difference_timestamp'].max(),3))
#        print('MIN t OFF surf CONSEC:\t', round(df_time_transition_FALSE2['difference_timestamp'].min(),3))
    
    

    print('GAZE % ON SURF:\t\t', round(percentage_on_surf,3),'%')
    print("")
    # Analisi dati csv fissazioni
    # Filtro tempi task
    filter_on_task_fix = (df_fix['world_timestamp'] >= start_time_task2) & (df_fix['world_timestamp'] <= stop_time_task2)
    df_fix2 = df_fix[filter_on_task_fix]

    # Filtro su superficie
    filter_on_surf_fix = (df_fix2['on_surf'])
    df_on_surf_fix = df_fix2[filter_on_surf_fix]

    dispersioneTot = 0
    distanzaMax = 0
    # Raggruppato per id calcolo la posizione media x,y di ogni fissazione per ogni campione 
    id_grouped = df_on_surf_fix.groupby(['fixation_id']).mean()

    for i in range (len(id_grouped)-1):
        distanzaX = (id_grouped['norm_pos_x'].values[i+1] - id_grouped['norm_pos_x'].values[i])**2
        distanzaY = (id_grouped['norm_pos_y'].values[i+1] - id_grouped['norm_pos_y'].values[i])**2
        distanza = math.sqrt(distanzaX + distanzaY)
        if distanza > distanzaMax:
            distanzaMax = distanza
        dispersioneTot += distanza
    
    # Calcolo la dispersione
    dispersioneMedia = dispersioneTot/(len(id_grouped)+1)

 
    
    # Statistiche fissazioni
    number_of_fix = len(set(df_on_surf_fix['fixation_id']))

    mean_fix_dur = id_grouped['duration'].mean() / 1000
    max_fix_dur = id_grouped['duration'].max() / 1000
    min_fix_dur = id_grouped['duration'].min() / 1000

    print('NUMBER ON-SURF FIX:\t', number_of_fix)
    print('MEAN FIXATION DURATION:\t', round(mean_fix_dur, 3), "s")
    print('MAX FIXATION DURATION:\t', round(max_fix_dur, 3), "s")
    print('MIN FIXATION DURATION: \t', round(min_fix_dur, 3), "s")
    print("MAX FIX DISTANCE:\t", round(distanzaMax, 3), "")
    print("MEAN DISTANCE:\t\t", round(dispersioneMedia, 3), "")
    print("PATH LENGTH:\t\t", round(dispersioneTot, 3), "")
    print("")


    # Analisi dati csv pupille
    filter_on_task_pupil = (df_pupil['pupil_timestamp'] >= start_time_task2) & (df_pupil['pupil_timestamp'] <= stop_time_task2)
    df_pupil2 = df_pupil[filter_on_task_pupil]
    
    filter_on_confidence = (df_pupil2['confidence'] >= 0.6)

    df_pupil3 = df_pupil2[filter_on_confidence]

    # raggruppo per occhio dx e sx
    eye_id_grouped = df_pupil3.groupby(['eye_id']).mean()
    # diameter_3d - diameter of the pupil scaled to mm based on anthropomorphic avg eye ball diameter and corrected for perspective.
    # diameter - diameter of the pupil in image pixels as observed in the eye image frame (is not corrected for perspective)
    
    mediaDimPupillaDx = eye_id_grouped['diameter_3d'].values[0]
    mediaDimPupillaSx = eye_id_grouped['diameter_3d'].values[1]
    #print(eye_id_grouped['diameter_3d'].values[0])
    #print(eye_id_grouped['diameter_3d'].values[1])
    mediaDimensionePupille = (mediaDimPupillaDx +mediaDimPupillaSx) / 2

    print("MEAN PUPILS DIMENSION:\t", round(mediaDimensionePupille,3), "mm")
    print("MAX PUPILS DIMENSION:\t", round(df_pupil3['diameter_3d'].max(),3), "mm")
    print("MIN PUPILS DIMENSION:\t", round(df_pupil3['diameter_3d'].min(),3), "mm")

print("--------------------------TOTALE----------------------------")
print("TEMPO TOTALE REG:\t", tempo_totale_registrazione)
print("TEMPO ON SURF REG:\t", tempo_on_surf_registrazione)
