.PHONY: prepare-components build-components

prepare-components:
	cd custom-elements && npm i

build-components:
	cd custom-elements && npm run build
	cp custom-elements/dist/assets/*.js src/untext/js/components.js
	cp custom-elements/dist/assets/*.css src/untext/css/components.css
