<?

$conf['endpoint']['local'] = 'http://sparql.tw.rpi.edu:3030/datafaqs/query';
$conf['endpoint']['biordf'] = 'http://biordf.net/sparql';
$conf['home'] = '/Applications/XAMPP/xamppfiles/htdocs/hello/lodspeakr/';
$conf['basedir'] = 'http://localhost/hello/';
$conf['debug'] = false;
$conf['mirror_external_uris'] = true;

/*ATTENTION: By default this application is available to
 * be exported and copied (its configuration)
 * by others. If you do not want that, 
 * turn the next option as false
 */ 
$conf['export'] = true;

#If you want to add/overrid a namespace, add it here
$conf['ns']['local']   = 'http://sparql.tw.rpi.edu/datafaqs/';
$conf['ns']['base']   = 'http://localhost/hello/';
?>
