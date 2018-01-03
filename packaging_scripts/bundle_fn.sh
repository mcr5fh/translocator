rm ~/$1.zip;
cd $(pwd)/node_modules;
zip -r9 ~/$1.zip * ;
cd ..;
zip -g ~/$1.zip $1.js;

# needed for the lambda
# filename.js
# node_modules/async
# node_modules/async/lib
# node_modules/async/lib/async.js
# node_modules/async/package.json