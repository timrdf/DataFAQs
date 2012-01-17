<?php
   require_once('c9d.php');
?>

<html> 
    <head>                                                                  
    <script type="text/javascript" src="jquery-1.7.1.js"></script>          
    <script type="text/javascript">                                         

$(document).ready(function() {

   $("a").click(function() {
      alert("Hello world!");
   });

});

    </script>                                                               
    </head>                                                              
    <body>                                                               
         <a href="">Link</a>
<?php
   $query = <<<______________________________
   prefix dcterms:    <http://purl.org/dc/terms/>
   prefix void:       <http://rdfs.org/ns/void#>

   select distinct ?subset max(?modified) as ?datetime
   WHERE {
     graph <http://logd.tw.rpi.edu/vocab/Dataset> {
       ?:dataset void:subset ?subset .
       optional { ?subset dcterms:modified ?modified }
     }
   } order by desc(?datetime)
______________________________;
   $DATASET_URI='http://logd.tw.rpi.edu/source/data-gov/dataset/4383/version/2011-Nov-29'
   $query = C9D::bind_variable($query,'?:dataset',$DATASET_URI);

   $ENDPOINT='http://logd.tw.rpi.edu/sparql'
   // TODO: echo '<code style="display:none">'.$query.'</code>';
   $result = C9D::request_query($query, $ENDPOINT);

   echo '<div>';
   if( isset($result['results']['bindings']) ) {
      echo '<table about="'.$DATASET_URI.'">';
      echo '  <tr><th>Subsets</th></tr>';
      foreach( $result['results']['bindings'] as $binding ) {
         $subset = $binding['subset']['value'];
         echo "  <tr>";
         echo "     <td property='conversion:todo'><a rel='conversion:todo' href='".$subset."'>".$subset."</a></td>";
         if( isset($binding['datetime']) ) {
            $date = $binding['datetime']['value'];
            echo "  <td property='conversion:todo'>".C9D::pretty_date($date)."</td>";
         }
         echo "  </tr>";
      }
      echo "</table>";
   }
   echo '</div>';
?>
    </body>                                                              
</html>

