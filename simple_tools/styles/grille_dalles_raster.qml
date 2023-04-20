<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="Symbology|Labeling|Fields|Forms|Actions|MapTips" version="3.16.16-Hannover" labelsEnabled="1">
  <renderer-v2 type="RuleRenderer" enableorderby="0" forceraster="0" symbollevels="0">
    <rules key="{cc831d53-19f9-4385-93c8-de664027f225}">
      <rule filter="True" label="TOUTES LES DALLES" checkstate="0" key="{9787b2c4-5c89-4ca9-aeee-314ee7e5e4ae}" symbol="0"/>
      <rule filter="doublon=1" label="Doublons" checkstate="0" key="{43fc460e-db1e-483b-964f-e3741c996cad}" symbol="1"/>
      <rule filter="doublon=0 or bordure=0" label="Masquer les doublons en bordure de zone" checkstate="0" key="{560775b6-a105-4be2-aaf2-c1d8d2ff823a}" symbol="2"/>
      <rule filter="doublon=0 or (bordure=0 and nuages=0)" label="Masquer les doublons en bordure de zone ou avec nuages" checkstate="0" key="{bdc10e04-96ef-4ca7-8ec9-85b702f0abb9}" symbol="3"/>
      <rule filter="inutile=1" label="Dalles inutiles car en doublon" checkstate="0" key="{f6a30a5b-10e6-45be-bbbc-3f1dfe681865}" symbol="4"/>
      <rule filter="inutile=0" label="Dalles utiles (inutile=0)" key="{c6ce72f7-0e11-40c7-8f58-ed8e532b588b}" symbol="5"/>
    </rules>
    <symbols>
      <symbol type="fill" name="0" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="254,0,225,118" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="82,82,82,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" name="1" clip_to_extent="1" alpha="0.6" force_rhr="0">
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="164,113,88,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="82,82,82,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" name="2" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="9,172,254,161" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="82,82,82,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" name="3" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="9,172,254,161" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="82,82,82,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol type="fill" name="4" clip_to_extent="1" alpha="0.6" force_rhr="0">
        <layer pass="0" class="CentroidFill" enabled="1" locked="0">
          <prop v="0" k="clip_on_current_part_only"/>
          <prop v="0" k="clip_points"/>
          <prop v="0" k="point_on_all_parts"/>
          <prop v="0" k="point_on_surface"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
          <symbol type="marker" name="@4@0" clip_to_extent="1" alpha="1" force_rhr="0">
            <layer pass="0" class="SimpleMarker" enabled="1" locked="0">
              <prop v="0" k="angle"/>
              <prop v="255,0,0,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="circle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="2" k="size"/>
              <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
              <prop v="MM" k="size_unit"/>
              <prop v="1" k="vertical_anchor_point"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol type="fill" name="5" clip_to_extent="1" alpha="1" force_rhr="0">
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="1,255,13,125" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="82,82,82,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontWordSpacing="0" textOrientation="horizontal" previewBkgrdColor="255,255,255,255" capitalization="0" namedStyle="Normal" blendMode="0" useSubstitutions="0" fontStrikeout="0" fontSize="8" fontItalic="0" fieldName="qualite" fontUnderline="0" fontWeight="50" allowHtml="0" fontLetterSpacing="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" fontSizeUnit="Point" textOpacity="1" isExpression="0" fontFamily="MS Shell Dlg 2" multilineHeight="1" fontKerning="1" textColor="0,0,0,255">
        <text-buffer bufferSizeUnits="MM" bufferBlendMode="0" bufferNoFill="1" bufferJoinStyle="128" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferSize="1" bufferDraw="0" bufferColor="255,255,255,255" bufferOpacity="1"/>
        <text-mask maskJoinStyle="128" maskSize="1.5" maskEnabled="0" maskType="0" maskOpacity="1" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskSizeUnits="MM"/>
        <background shapeOffsetX="0" shapeOffsetUnit="MM" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64" shapeBlendMode="0" shapeFillColor="255,255,255,255" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiY="0" shapeType="0" shapeSVGFile="" shapeRotationType="0" shapeSizeType="0" shapeOpacity="1" shapeSizeUnit="MM" shapeOffsetY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeSizeX="0" shapeBorderColor="128,128,128,255" shapeBorderWidth="0" shapeDraw="0" shapeRotation="0" shapeRadiiUnit="MM" shapeBorderWidthUnit="MM" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRadiiX="0" shapeSizeY="0">
          <symbol type="marker" name="markerSymbol" clip_to_extent="1" alpha="0.6" force_rhr="0">
            <layer pass="0" class="SimpleMarker" enabled="1" locked="0">
              <prop v="0" k="angle"/>
              <prop v="243,166,178,255" k="color"/>
              <prop v="1" k="horizontal_anchor_point"/>
              <prop v="bevel" k="joinstyle"/>
              <prop v="circle" k="name"/>
              <prop v="0,0" k="offset"/>
              <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
              <prop v="MM" k="offset_unit"/>
              <prop v="35,35,35,255" k="outline_color"/>
              <prop v="solid" k="outline_style"/>
              <prop v="0" k="outline_width"/>
              <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
              <prop v="MM" k="outline_width_unit"/>
              <prop v="diameter" k="scale_method"/>
              <prop v="2" k="size"/>
              <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
              <prop v="MM" k="size_unit"/>
              <prop v="1" k="vertical_anchor_point"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option type="QString" name="name" value=""/>
                  <Option name="properties"/>
                  <Option type="QString" name="type" value="collection"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.7" shadowRadius="1.5" shadowColor="0,0,0,255" shadowOffsetUnit="MM" shadowScale="100" shadowBlendMode="6" shadowOffsetGlobal="1" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowDraw="0" shadowUnder="0" shadowOffsetDist="1" shadowRadiusUnit="MM" shadowRadiusAlphaOnly="0"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format reverseDirectionSymbol="0" placeDirectionSymbol="0" rightDirectionSymbol=">" useMaxLineLengthForAutoWrap="1" autoWrapLength="0" formatNumbers="0" multilineAlign="3" plussign="0" leftDirectionSymbol="&lt;" wrapChar="" addDirectionSymbol="0" decimals="3"/>
      <placement xOffset="0" distMapUnitScale="3x:0,0,0,0,0,0" offsetType="0" lineAnchorPercent="0.5" rotationAngle="0" overrunDistanceUnit="MM" polygonPlacementFlags="2" overrunDistance="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="25" repeatDistanceUnits="MM" maxCurvedCharAngleOut="-25" geometryGeneratorType="PointGeometry" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" placement="1" priority="5" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" preserveRotation="1" layerType="PolygonGeometry" placementFlags="10" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" centroidInside="0" geometryGenerator="" lineAnchorType="0" offsetUnits="MM" dist="0" geometryGeneratorEnabled="0" yOffset="0" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" quadOffset="4" centroidWhole="0" distUnits="MM" repeatDistance="0"/>
      <rendering obstacle="1" scaleMax="100000" obstacleFactor="1" maxNumLabels="2000" fontMinPixelSize="3" scaleVisibility="1" limitNumLabels="0" obstacleType="1" minFeatureSize="0" scaleMin="0" labelPerPart="0" fontMaxPixelSize="10000" displayAll="0" drawLabels="1" upsidedownLabels="0" mergeLines="0" fontLimitPixelSize="0" zIndex="0"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" name="anchorPoint" value="pole_of_inaccessibility"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
          <Option type="bool" name="drawToAllParts" value="false"/>
          <Option type="QString" name="enabled" value="0"/>
          <Option type="QString" name="labelAnchorPoint" value="point_on_exterior"/>
          <Option type="QString" name="lineSymbol" value="&lt;symbol type=&quot;line&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; alpha=&quot;1&quot; force_rhr=&quot;0&quot;>&lt;layer pass=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot; locked=&quot;0&quot;>&lt;prop v=&quot;0&quot; k=&quot;align_dash_pattern&quot;/>&lt;prop v=&quot;square&quot; k=&quot;capstyle&quot;/>&lt;prop v=&quot;5;2&quot; k=&quot;customdash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;customdash_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;customdash_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;dash_pattern_offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;dash_pattern_offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;dash_pattern_offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;draw_inside_polygon&quot;/>&lt;prop v=&quot;bevel&quot; k=&quot;joinstyle&quot;/>&lt;prop v=&quot;60,60,60,255&quot; k=&quot;line_color&quot;/>&lt;prop v=&quot;solid&quot; k=&quot;line_style&quot;/>&lt;prop v=&quot;0.3&quot; k=&quot;line_width&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;line_width_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;offset&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;offset_map_unit_scale&quot;/>&lt;prop v=&quot;MM&quot; k=&quot;offset_unit&quot;/>&lt;prop v=&quot;0&quot; k=&quot;ring_filter&quot;/>&lt;prop v=&quot;0&quot; k=&quot;tweak_dash_pattern_on_corners&quot;/>&lt;prop v=&quot;0&quot; k=&quot;use_custom_dash&quot;/>&lt;prop v=&quot;3x:0,0,0,0,0,0&quot; k=&quot;width_map_unit_scale&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
          <Option type="double" name="minLength" value="0"/>
          <Option type="QString" name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="minLengthUnit" value="MM"/>
          <Option type="double" name="offsetFromAnchor" value="0"/>
          <Option type="QString" name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromAnchorUnit" value="MM"/>
          <Option type="double" name="offsetFromLabel" value="0"/>
          <Option type="QString" name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromLabelUnit" value="MM"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <fieldConfiguration>
    <field configurationFlags="None" name="fid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="fichier">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="xmin">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="ymax">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="date">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="dossier">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="chemin">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="doublon">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="bordure">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="nuages">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="qualite">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="inutile">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="fid" name="" index="0"/>
    <alias field="fichier" name="" index="1"/>
    <alias field="xmin" name="" index="2"/>
    <alias field="ymax" name="" index="3"/>
    <alias field="date" name="" index="4"/>
    <alias field="dossier" name="" index="5"/>
    <alias field="chemin" name="" index="6"/>
    <alias field="doublon" name="" index="7"/>
    <alias field="bordure" name="" index="8"/>
    <alias field="nuages" name="" index="9"/>
    <alias field="qualite" name="" index="10"/>
    <alias field="inutile" name="" index="11"/>
  </aliases>
  <defaults>
    <default field="fid" applyOnUpdate="0" expression=""/>
    <default field="fichier" applyOnUpdate="0" expression=""/>
    <default field="xmin" applyOnUpdate="0" expression=""/>
    <default field="ymax" applyOnUpdate="0" expression=""/>
    <default field="date" applyOnUpdate="0" expression=""/>
    <default field="dossier" applyOnUpdate="0" expression=""/>
    <default field="chemin" applyOnUpdate="0" expression=""/>
    <default field="doublon" applyOnUpdate="0" expression=""/>
    <default field="bordure" applyOnUpdate="0" expression=""/>
    <default field="nuages" applyOnUpdate="0" expression=""/>
    <default field="qualite" applyOnUpdate="0" expression=""/>
    <default field="inutile" applyOnUpdate="0" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="fid" constraints="3" notnull_strength="1" unique_strength="1"/>
    <constraint exp_strength="0" field="fichier" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="xmin" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="ymax" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="date" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="dossier" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="chemin" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="doublon" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="bordure" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="nuages" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="qualite" constraints="0" notnull_strength="0" unique_strength="0"/>
    <constraint exp_strength="0" field="inutile" constraints="0" notnull_strength="0" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="fid" desc="" exp=""/>
    <constraint field="fichier" desc="" exp=""/>
    <constraint field="xmin" desc="" exp=""/>
    <constraint field="ymax" desc="" exp=""/>
    <constraint field="date" desc="" exp=""/>
    <constraint field="dossier" desc="" exp=""/>
    <constraint field="chemin" desc="" exp=""/>
    <constraint field="doublon" desc="" exp=""/>
    <constraint field="bordure" desc="" exp=""/>
    <constraint field="nuages" desc="" exp=""/>
    <constraint field="qualite" desc="" exp=""/>
    <constraint field="inutile" desc="" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{57933694-638a-4daa-a2d5-4b685190d020}"/>
    <actionsetting shortTitle="" type="1" name="Afficher la dalle" notificationMessage="" isEnabledOnlyWhenEditable="0" action="layer = qgis.utils.iface.activeLayer()&#xd;&#xa;qgis.utils.iface.addRasterLayer(r&quot;[%chemin%]&quot;,&quot;[%fichier%]&quot;)&#xd;&#xa;qgis.utils.iface.setActiveLayer(layer)" icon="" capture="0" id="{e3fe38dc-3a05-4aa7-92c2-7a6e5d07f7e3}">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting shortTitle="" type="1" name="Ouvrir TOUTES les dalles du dossier" notificationMessage="" isEnabledOnlyWhenEditable="0" action="msgBar = qgis.utils.iface.messageBar()&#xd;&#xa;msgBar.pushMessage(&quot;Patientez pendant l'ouverture des dalles...&quot;,Qgis.Info,0)&#xd;&#xa;QgsApplication.processEvents() # Pour afficher le msg MAINTENANT&#xd;&#xa;layer = qgis.utils.iface.activeLayer()&#xd;&#xa;root = qgis.utils.iface.layerTreeView().currentGroupNode()&#xd;&#xa;grp = root.insertGroup(0,r&quot;[%dossier%]&quot;)&#xd;&#xa;grp.setItemVisibilityChecked(False)&#xd;&#xa;for feat in layer.getFeatures():&#xd;&#xa;&#x9;if feat['dossier']!=r&quot;[%dossier%]&quot;: continue&#xd;&#xa;&#x9;lay = QgsRasterLayer(feat['chemin'],feat['fichier'])&#xd;&#xa;&#x9;QgsProject.instance().addMapLayer(lay, False)&#xd;&#xa;&#x9;grp.addLayer(lay)&#xd;&#xa;&#xd;&#xa;qgis.utils.iface.setActiveLayer(layer)&#xd;&#xa;grp.setExpanded(False)&#xd;&#xa;grp.setItemVisibilityChecked(True)&#xd;&#xa;msgBar.clearWidgets()&#xd;&#xa;msgBar.pushMessage(&quot;Les dalles sont affichées dans le groupe : [%dossier%]&quot;,Qgis.Success,10)&#xd;&#xa;" icon="" capture="0" id="{ca3a8c76-1b30-40b0-a410-9bbfec424cb4}">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
    <actionsetting shortTitle="" type="1" name="Ouvrir les dalles UTILES du dossier (inutile=0)" notificationMessage="" isEnabledOnlyWhenEditable="0" action="msgBar = qgis.utils.iface.messageBar()&#xd;&#xa;layer = qgis.utils.iface.activeLayer()&#xd;&#xa;champs = layer.fields().names()&#xd;&#xa;if not 'inutile' in champs:&#xd;&#xa;&#x9;msgBar.pushMessage('Impossible: la couche {} n\'a pas le champ : &quot;inutile&quot;'.format(layer.name()),Qgis.Warning,10)&#xd;&#xa;else:&#xd;&#xa;&#x9;msgBar.pushMessage(&quot;Patientez pendant l'ouverture des dalles...&quot;,Qgis.Info,0)&#xd;&#xa;&#x9;root = qgis.utils.iface.layerTreeView().currentGroupNode()&#xd;&#xa;&#x9;grp = root.insertGroup(0,r&quot;[%dossier%]&quot;)&#xd;&#xa;&#x9;grp.setItemVisibilityChecked(False)&#xd;&#xa;&#x9;QgsApplication.processEvents() # Pour afficher le msg MAINTENANT&#xd;&#xa;&#x9;for feat in layer.getFeatures():&#xd;&#xa;&#x9;&#x9;if feat['dossier']!=r&quot;[%dossier%]&quot;: continue&#xd;&#xa;&#x9;&#x9;if feat['inutile']==1: continue&#xd;&#xa;&#x9;&#x9;lay = QgsRasterLayer(feat['chemin'],feat['fichier'])&#xd;&#xa;&#x9;&#x9;QgsProject.instance().addMapLayer(lay, False)&#xd;&#xa;&#x9;&#x9;grp.addLayer(lay)&#xd;&#xa;&#xd;&#xa;&#x9;qgis.utils.iface.setActiveLayer(layer)&#xd;&#xa;&#x9;grp.setExpanded(False)&#xd;&#xa;&#x9;grp.setItemVisibilityChecked(True)&#xd;&#xa;&#x9;msgBar.clearWidgets()&#xd;&#xa;&#x9;msgBar.pushMessage(&quot;Les dalles sont affichées dans le groupe : [%dossier%]&quot;,Qgis.Success,10)&#xd;&#xa;" icon="" capture="0" id="{1ffca7cf-aec0-4598-8d56-991749398fa5}">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
Les formulaires QGIS peuvent avoir une fonction Python qui sera appelée à l'ouverture du formulaire.

Utilisez cette fonction pour ajouter plus de fonctionnalités à vos formulaires.

Entrez le nom de la fonction dans le champ "Fonction d'initialisation Python".
Voici un exemple à suivre:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")

]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="bordure" editable="1"/>
    <field name="chemin" editable="1"/>
    <field name="date" editable="1"/>
    <field name="dossier" editable="1"/>
    <field name="doublon" editable="1"/>
    <field name="fichier" editable="1"/>
    <field name="fid" editable="1"/>
    <field name="inutile" editable="1"/>
    <field name="nuages" editable="1"/>
    <field name="qualite" editable="1"/>
    <field name="utiliser" editable="1"/>
    <field name="xmin" editable="1"/>
    <field name="ymax" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="bordure" labelOnTop="0"/>
    <field name="chemin" labelOnTop="0"/>
    <field name="date" labelOnTop="0"/>
    <field name="dossier" labelOnTop="0"/>
    <field name="doublon" labelOnTop="0"/>
    <field name="fichier" labelOnTop="0"/>
    <field name="fid" labelOnTop="0"/>
    <field name="inutile" labelOnTop="0"/>
    <field name="nuages" labelOnTop="0"/>
    <field name="qualite" labelOnTop="0"/>
    <field name="utiliser" labelOnTop="0"/>
    <field name="xmin" labelOnTop="0"/>
    <field name="ymax" labelOnTop="0"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
