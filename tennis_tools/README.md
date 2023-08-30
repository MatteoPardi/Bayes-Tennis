## Quick guide notebook


```python
from tennis_tools import TennisUniverse
```

### Load Data

- single file


```python
tu = TennisUniverse('data_1.csv')
tu
```




    TennisUniverse
      files: ['data_1.csv']
      n_accepted_rows: 130
      n_rejected_rows: 2
      n_players: 94
      tournaments:
        - 'Mr. Dodo 22'
        - 'Mr. Dodo 22 - Fase Eliminatoria'



- more files


```python
tu = TennisUniverse('data_1.csv', 'data_2.csv', 'other_data.csv')
tu
```




    TennisUniverse
      files: ['data_1.csv', 'data_2.csv', 'other_data.csv']
      n_accepted_rows: 649
      n_rejected_rows: 9
      n_players: 188
      tournaments:
        - 'Mr. Dodo 22'
        - 'Mr. Dodo 22 - Fase Eliminatoria'
        - 'AICS 2023'
        - 'Mr. Dodo 23 - Fase Eliminatoria'
        - 'Mr. Dodo 23'



- 'star' notation


```python
tu = TennisUniverse('data_*.csv', 'other_data.csv')
tu
```




    TennisUniverse
      files: ['data_1.csv', 'data_2.csv', 'other_data.csv']
      n_accepted_rows: 649
      n_rejected_rows: 9
      n_players: 188
      tournaments:
        - 'Mr. Dodo 22'
        - 'Mr. Dodo 22 - Fase Eliminatoria'
        - 'AICS 2023'
        - 'Mr. Dodo 23 - Fase Eliminatoria'
        - 'Mr. Dodo 23'



### Check Rejected Rows


```python
tu.rejected
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>error_type</th>
    </tr>
    <tr>
      <th>file</th>
      <th>file_row</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="2" valign="top">data_1.csv</th>
      <th>35</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th>126</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th rowspan="3" valign="top">data_2.csv</th>
      <th>102</th>
      <td>players not admittable</td>
    </tr>
    <tr>
      <th>223</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th>272</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th rowspan="4" valign="top">other_data.csv</th>
      <th>37</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th>44</th>
      <td>players not admittable</td>
    </tr>
    <tr>
      <th>151</th>
      <td>score not admittable</td>
    </tr>
    <tr>
      <th>242</th>
      <td>score not admittable</td>
    </tr>
  </tbody>
</table>
</div>



### View Loaded Data


```python
tu.df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>players A</th>
      <th>players B</th>
      <th>score</th>
      <th>tournament</th>
    </tr>
    <tr>
      <th>file</th>
      <th>file_row</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">data_1.csv</th>
      <th>0</th>
      <td>Pierluigi Pacomio</td>
      <td>Fulvio Zoppetti</td>
      <td>1-6 2-6</td>
      <td>Mr. Dodo 22</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Telemaco Pizzetti, Baldassare Nosiglia</td>
      <td>Atenulf Solimena, Lucio Conte</td>
      <td>4-6 2-6</td>
      <td>Mr. Dodo 22</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Vittorio Giannuzzi</td>
      <td>Ippazio Milanesi</td>
      <td>7-6 6-4</td>
      <td>Mr. Dodo 22</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Gabriele Fantoni</td>
      <td>Domenico Cusano</td>
      <td>6-0 6-0</td>
      <td>Mr. Dodo 22</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Cirillo Pisaroni</td>
      <td>Ugolino Ricciardi</td>
      <td>6-2 6-0</td>
      <td>Mr. Dodo 22</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">other_data.csv</th>
      <th>243</th>
      <td>Fulvio Zoppetti</td>
      <td>Gianni Guarana</td>
      <td>5-7 2-6</td>
      <td>Mr. Dodo 22 - Fase Eliminatoria</td>
    </tr>
    <tr>
      <th>244</th>
      <td>Atenulf Solimena, Adriano Spinelli</td>
      <td>Giacinto Orengo, Manuel Cannizzaro</td>
      <td>5-7 3-6</td>
      <td>Mr. Dodo 22 - Fase Eliminatoria</td>
    </tr>
    <tr>
      <th>245</th>
      <td>Gabriele Fantoni</td>
      <td>Ennio Rizzoli</td>
      <td>3-6 7-6 7-10</td>
      <td>Mr. Dodo 22 - Fase Eliminatoria</td>
    </tr>
    <tr>
      <th>246</th>
      <td>Manuel Cannizzaro</td>
      <td>Pasqual Dovara</td>
      <td>6-3 7-6</td>
      <td>Mr. Dodo 22 - Fase Eliminatoria</td>
    </tr>
    <tr>
      <th>247</th>
      <td>Donato Cattaneo, Sebastiano Alfieri</td>
      <td>Ubaldo Ramazzotti, Gioffre Farina</td>
      <td>6-3 6-3</td>
      <td>Mr. Dodo 22 - Fase Eliminatoria</td>
    </tr>
  </tbody>
</table>
<p>658 rows × 4 columns</p>
</div>




```python
tu.n_players
```




    188




```python
tu.players
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>player</th>
    </tr>
    <tr>
      <th>player_idx</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Pierluigi Pacomio</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Fulvio Zoppetti</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Telemaco Pizzetti</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Baldassare Nosiglia</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Atenulf Solimena</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th>183</th>
      <td>Biagio Franceschi</td>
    </tr>
    <tr>
      <th>184</th>
      <td>Agnolo Conti</td>
    </tr>
    <tr>
      <th>185</th>
      <td>Nanni Lucchesi</td>
    </tr>
    <tr>
      <th>186</th>
      <td>Benvenuto Armellini</td>
    </tr>
    <tr>
      <th>187</th>
      <td>Ugo Taliercio</td>
    </tr>
  </tbody>
</table>
<p>188 rows × 1 columns</p>
</div>



### Ranking (Not Optimized Yet)


```python
tu.ranking
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>player</th>
      <th>ability</th>
      <th>n_singles</th>
      <th>n_doubles</th>
      <th>n_tot</th>
    </tr>
    <tr>
      <th>rank</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Pierluigi Pacomio</td>
      <td>100.0</td>
      <td>21</td>
      <td>7</td>
      <td>28</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Fulvio Zoppetti</td>
      <td>100.0</td>
      <td>15</td>
      <td>9</td>
      <td>24</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Telemaco Pizzetti</td>
      <td>100.0</td>
      <td>0</td>
      <td>11</td>
      <td>11</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Baldassare Nosiglia</td>
      <td>100.0</td>
      <td>10</td>
      <td>10</td>
      <td>20</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Atenulf Solimena</td>
      <td>100.0</td>
      <td>0</td>
      <td>22</td>
      <td>22</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>184</th>
      <td>Biagio Franceschi</td>
      <td>100.0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>185</th>
      <td>Agnolo Conti</td>
      <td>100.0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>186</th>
      <td>Nanni Lucchesi</td>
      <td>100.0</td>
      <td>0</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>187</th>
      <td>Benvenuto Armellini</td>
      <td>100.0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
    <tr>
      <th>188</th>
      <td>Ugo Taliercio</td>
      <td>100.0</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
<p>188 rows × 5 columns</p>
</div>



### Optimization

To modify the loss function, you have to modify the source code. To just see how it's defined by default:


```python
print(tu.loss)
```

    Loss Function. Terms:
    regularization: L2_Regularization(bandwidth=5.0)
    mrdodo: LogLikelihoodTerm:
      scoring_system: 'MrDodo'
      n_samples: 649
    


```python
'''
tu.optimize (n_iter=3000, 
             lr_start=1e-1, 
             lr_end=1e-3, 
             half_time=10, 
             months_shift='last played',
             device='cpu', # choose 'cuda' to work with GPU
             verbose=100):
'''
tu.optimize()
```

    (tic)
    Optimization started. n_iter = 3000
     n 0: loss = 2229.3115234375
     n 100: loss = 1654.361328125
     n 200: loss = 1651.0430908203125
     n 300: loss = 1650.776611328125
     n 400: loss = 1650.7396240234375
     n 500: loss = 1650.7330322265625
     n 600: loss = 1650.7315673828125
     n 700: loss = 1650.731201171875
     n 800: loss = 1650.7310791015625
     n 900: loss = 1650.7310791015625
     n 1000: loss = 1650.7310791015625
     n 1100: loss = 1650.73095703125
     n 1200: loss = 1650.731201171875
     n 1300: loss = 1650.7310791015625
     n 1400: loss = 1650.73095703125
     n 1500: loss = 1650.73095703125
     n 1600: loss = 1650.73095703125
     n 1700: loss = 1650.73095703125
     n 1800: loss = 1650.73095703125
     n 1900: loss = 1650.73095703125
     n 2000: loss = 1650.7310791015625
     n 2100: loss = 1650.7310791015625
     n 2200: loss = 1650.7310791015625
     n 2300: loss = 1650.7310791015625
     n 2400: loss = 1650.7310791015625
     n 2500: loss = 1650.7310791015625
     n 2600: loss = 1650.7310791015625
     n 2700: loss = 1650.7310791015625
     n 2800: loss = 1650.7310791015625
     n 2900: loss = 1650.7310791015625
     n 3000: loss = 1650.7310791015625 (end)
    (toc) 14.73 s
    

### Ranking (Optimized)


```python
tu.ranking
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>player</th>
      <th>ability</th>
      <th>n_singles</th>
      <th>n_doubles</th>
      <th>n_tot</th>
    </tr>
    <tr>
      <th>rank</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>Salvatore Malaparte</td>
      <td>106.692085</td>
      <td>0</td>
      <td>5</td>
      <td>5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Ottone Basadonna</td>
      <td>106.272957</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Cirillo Pisaroni</td>
      <td>105.739639</td>
      <td>17</td>
      <td>3</td>
      <td>20</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Gioacchino Flaiano</td>
      <td>105.717369</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Giuseppe Cavalcanti</td>
      <td>105.717369</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>184</th>
      <td>Domenico Cusano</td>
      <td>93.604691</td>
      <td>6</td>
      <td>3</td>
      <td>9</td>
    </tr>
    <tr>
      <th>185</th>
      <td>Valerio Aporti</td>
      <td>92.754433</td>
      <td>3</td>
      <td>4</td>
      <td>7</td>
    </tr>
    <tr>
      <th>186</th>
      <td>Lazzaro Luna</td>
      <td>92.728943</td>
      <td>3</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>187</th>
      <td>Gionata Gulotta</td>
      <td>90.980530</td>
      <td>3</td>
      <td>0</td>
      <td>3</td>
    </tr>
    <tr>
      <th>188</th>
      <td>Ranieri Trapani</td>
      <td>90.038269</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
    </tr>
  </tbody>
</table>
<p>188 rows × 5 columns</p>
</div>



### Save Ranking


```python
tu.save("ranking.xlsx") # or "ranking.csv"
```
